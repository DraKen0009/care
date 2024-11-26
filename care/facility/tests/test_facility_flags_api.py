from rest_framework import status
from rest_framework.test import APITestCase

from care.facility.models import FacilityFlag
from care.utils.registries.feature_flag import FlagRegistry, FlagType
from care.utils.tests.test_utils import TestUtils


class FacilityFlagsViewSetTestCase(TestUtils, APITestCase):
    @classmethod
    def setUpTestData(cls):
        FlagRegistry.register(FlagType.FACILITY, "TEST_FLAG")
        FlagRegistry.register(FlagType.FACILITY, "TEST_FLAG_2")

        cls.state = cls.create_state()
        cls.district = cls.create_district(cls.state)
        cls.local_body = cls.create_local_body(cls.district)
        cls.super_user = cls.create_super_user("su", cls.district)
        cls.facility = cls.create_facility(cls.super_user, cls.district, cls.local_body)
        cls.facility2 = cls.create_facility(
            cls.super_user, cls.district, cls.local_body
        )
        cls.user = cls.create_user("staff", cls.district, home_facility=cls.facility)
        cls.facility_flag_2 = cls.create_facility_flag("TEST_FLAG_2", cls.facility)

    def setUp(self):
        self.facility_flag_1 = self.create_facility_flag("TEST_FLAG", self.facility)

    def get_url(self, facility_flag_id=None, action=None):
        base_url = "/api/v1/facility_flags/"
        if facility_flag_id is not None:
            base_url += f"{facility_flag_id}/"
        if action is not None:
            base_url += f"{action}/"
        return base_url

    def test_access_with_non_super_user(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_access_with_super_user(self):
        self.client.force_authenticate(user=self.super_user)
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_facility_flags(self):
        self.client.force_authenticate(user=self.super_user)
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["count"], 2)

    def test_list_available_flags(self):
        self.client.force_authenticate(user=self.super_user)
        response = self.client.get(self.get_url(action="available-flags"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(sorted(data["available_flags"]), ["TEST_FLAG", "TEST_FLAG_2"])

    def test_create_facility_flag(self):
        self.client.force_authenticate(user=self.super_user)

        response = self.client.post(self.get_url(), {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("This field is required.", response.json()["flag"])
        self.assertIn("This field is required.", response.json()["facility"])

        # Attempting to create a duplicate flag
        response = self.client.post(
            self.get_url(), {"flag": "TEST_FLAG", "facility": self.facility.external_id}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "The fields facility, flag must make a unique set.",
            response.json()["non_field_errors"],
        )

        # Creating a new facility flag
        response = self.client.post(
            self.get_url(),
            {"flag": "TEST_FLAG", "facility": self.facility2.external_id},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_retrieve_facility_flag(self):
        self.client.force_authenticate(user=self.super_user)
        response = self.client.get(self.get_url(self.facility_flag_1.external_id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["flag"], "TEST_FLAG")
        self.assertEqual(data["facility"], str(self.facility.external_id))

    def test_update_facility_flag(self):
        self.client.force_authenticate(user=self.super_user)

        # Confirming original values
        response = self.client.get(self.get_url(self.facility_flag_1.external_id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["flag"], "TEST_FLAG")
        self.assertEqual(data["facility"], str(self.facility.external_id))

        # Update the facility flag
        response = self.client.put(
            self.get_url(self.facility_flag_1.external_id),
            {"flag": "TEST_FLAG", "facility": self.facility2.external_id},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.facility_flag_1.refresh_from_db()
        self.assertEqual(self.facility_flag_1.flag, "TEST_FLAG")
        self.assertEqual(
            self.facility_flag_1.facility.external_id, self.facility2.external_id
        )

    def test_patch_facility_flag(self):
        self.client.force_authenticate(user=self.super_user)

        # Confirming original values
        response = self.client.get(self.get_url(self.facility_flag_1.external_id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["flag"], "TEST_FLAG")
        self.assertEqual(data["facility"], str(self.facility.external_id))

        # Patch the facility flag
        response = self.client.patch(
            self.get_url(self.facility_flag_1.external_id),
            {"facility": self.facility2.external_id},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.facility_flag_1.refresh_from_db()
        self.assertEqual(self.facility_flag_1.flag, "TEST_FLAG")
        self.assertEqual(
            self.facility_flag_1.facility.external_id, self.facility2.external_id
        )

    def test_delete_facility_flag(self):
        self.client.force_authenticate(user=self.super_user)

        # Confirm if the object exist
        self.assertTrue(
            FacilityFlag.objects.filter(
                external_id=self.facility_flag_1.external_id
            ).exists()
        )
        response = self.client.delete(self.get_url(self.facility_flag_1.external_id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.facility_flag_1.refresh_from_db()
        self.assertFalse(
            FacilityFlag.objects.filter(
                external_id=self.facility_flag_1.external_id
            ).exists()
        )

    def test_creating_facility_flag_with_non_existing_flag(self):
        self.client.force_authenticate(user=self.super_user)

        response = self.client.post(
            self.get_url(),
            {"flag": "TEST_FLAG_NON_EXISTING", "facility": self.facility2.external_id},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()["detail"], "Flag not registered")
