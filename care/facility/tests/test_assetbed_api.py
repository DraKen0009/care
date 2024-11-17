from rest_framework import status
from rest_framework.test import APITestCase

from care.facility.models import AssetBed, Bed
from care.utils.assetintegration.asset_classes import AssetClasses
from care.utils.tests.test_utils import TestUtils


class AssetBedViewSetTests(TestUtils, APITestCase):
    """
    Test class for AssetBed
    """

    @classmethod
    def setUpTestData(cls) -> None:
        cls.state = cls.create_state()
        cls.district = cls.create_district(cls.state)
        cls.local_body = cls.create_local_body(cls.district)
        cls.super_user = cls.create_super_user("su", cls.district)
        cls.facility = cls.create_facility(cls.super_user, cls.district, cls.local_body)
        cls.facility2 = cls.create_facility(
            cls.super_user, cls.district, cls.local_body
        )
        cls.user = cls.create_user(
            "user",
            district=cls.district,
            local_body=cls.local_body,
            home_facility=cls.facility,
        )  # user from facility
        cls.foreign_user = cls.create_user(
            "foreign_user",
            district=cls.district,
            local_body=cls.local_body,
            home_facility=cls.facility2,
        )  # user outside the facility
        cls.patient = cls.create_patient(
            cls.district, cls.facility, local_body=cls.local_body
        )
        cls.asset_location1 = cls.create_asset_location(cls.facility)
        cls.asset1 = cls.create_asset(
            cls.asset_location1, asset_class=AssetClasses.HL7MONITOR.name
        )
        cls.bed1 = Bed.objects.create(
            name="bed1", location=cls.asset_location1, facility=cls.facility
        )
        cls.asset_location2 = cls.create_asset_location(cls.facility)
        cls.asset_location3 = cls.create_asset_location(cls.facility)
        cls.asset3 = cls.create_asset(
            cls.asset_location3, asset_class=AssetClasses.VENTILATOR.name
        )
        cls.bed3 = Bed.objects.create(
            name="bed3", location=cls.asset_location3, facility=cls.facility
        )
        # for testing create, put and patch requests
        cls.bed4 = Bed.objects.create(
            name="bed4", location=cls.asset_location3, facility=cls.facility
        )
        cls.foreign_asset_location = cls.create_asset_location(cls.facility2)
        cls.foreign_asset = cls.create_asset(cls.foreign_asset_location)
        cls.foreign_bed = Bed.objects.create(
            name="foreign_bed",
            location=cls.foreign_asset_location,
            facility=cls.facility2,
        )

        cls.create_assetbed(bed=cls.bed3, asset=cls.asset3)

        # assetbed for different facility
        cls.create_assetbed(bed=cls.foreign_bed, asset=cls.foreign_asset)

    def setUp(self) -> None:
        super().setUp()
        self.assetbed = self.create_assetbed(bed=self.bed1, asset=self.asset1)

    def get_base_url(self) -> str:
        return "/api/v1/assetbed"

    def get_url(self, external_id=None):
        """
        Constructs the url for assetbed api
        """
        base_url = f"{self.get_base_url()}/"
        if external_id is not None:
            base_url += f"{external_id}/"
        return base_url

    def test_list_assetbed(self):
        # assetbed accessible to facility 1 user (current user)
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

        # logging in as foreign user
        self.client.force_login(self.foreign_user)

        # assetbed accessible to facility 2 user (foreign user)
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

        # logging in as superuser
        self.client.force_login(self.super_user)

        # access to all assetbed
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], AssetBed.objects.count())

        # testing for filters
        response = self.client.get(self.get_url(), {"asset": self.asset1.external_id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["count"], AssetBed.objects.filter(asset=self.asset1).count()
        )

        response = self.client.get(self.get_url(), {"bed": self.bed1.external_id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["count"], AssetBed.objects.filter(bed=self.bed1).count()
        )
        self.assertEqual(
            response.data["results"][0]["bed_object"]["name"], self.bed1.name
        )

        response = self.client.get(
            self.get_url(), {"facility": self.facility.external_id}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["count"],
            AssetBed.objects.filter(bed__facility=self.facility).count(),
        )

    def test_create_assetbed(self):
        # Missing asset and bed
        missing_fields_data = {}
        response = self.client.post(self.get_url(), missing_fields_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("asset", response.data)
        self.assertIn("bed", response.data)

        # Invalid asset UUID
        invalid_asset_uuid_data = {
            "asset": "invalid-uuid",
            "bed": str(self.bed1.external_id),
        }
        response = self.client.post(
            self.get_url(), invalid_asset_uuid_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("asset", response.data)

        # Invalid bed UUID
        invalid_bed_uuid_data = {
            "asset": str(self.asset1.external_id),
            "bed": "invalid-uuid",
        }
        response = self.client.post(
            self.get_url(), invalid_bed_uuid_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("bed", response.data)

        # Non-existent asset UUID
        non_existent_asset_uuid_data = {
            "asset": "11111111-1111-1111-1111-111111111111",
            "bed": str(self.bed1.external_id),
        }
        response = self.client.post(
            self.get_url(), non_existent_asset_uuid_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Non-existent bed UUID
        non_existent_bed_uuid_data = {
            "asset": str(self.asset1.external_id),
            "bed": "11111111-1111-1111-1111-111111111111",
        }
        response = self.client.post(
            self.get_url(), non_existent_bed_uuid_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # User does not have access to foreign facility
        foreign_user_data = {
            "asset": str(self.foreign_asset.external_id),
            "bed": str(self.foreign_bed.external_id),
        }
        self.client.force_login(self.user)  # Ensure current user is logged in
        response = self.client.post(self.get_url(), foreign_user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Invalid asset class (e.g., VENTILATOR)
        invalid_asset_class_data = {
            "asset": str(self.asset3.external_id),  # VENTILATOR asset class
            "bed": str(self.bed1.external_id),
        }
        response = self.client.post(
            self.get_url(), invalid_asset_class_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("asset", response.data)

        # Asset and bed in different facilities
        asset_bed_different_facilities = {
            "asset": str(self.foreign_asset.external_id),
            "bed": str(self.bed1.external_id),
        }
        response = self.client.post(
            self.get_url(), asset_bed_different_facilities, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Trying to create a duplicate assetbed with bed3 and asset3 (assetbed already exists)
        duplicate_asset_class_data = {
            "asset": str(self.asset3.external_id),
            "bed": str(self.bed3.external_id),
        }
        response = self.client.post(
            self.get_url(), duplicate_asset_class_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Successfully create AssetBed with valid data
        valid_data = {
            "asset": str(self.asset1.external_id),
            "bed": str(self.bed4.external_id),
        }
        response = self.client.post(self.get_url(), valid_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_retrieve_assetbed(self):
        response = self.client.get(self.get_url(external_id=self.assetbed.external_id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["asset_object"]["id"], str(self.assetbed.asset.external_id)
        )
        self.assertEqual(
            response.data["bed_object"]["id"], str(self.assetbed.bed.external_id)
        )

    def test_update_assetbed(self):
        # checking old values
        response = self.client.get(self.get_url(external_id=self.assetbed.external_id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["meta"], {})
        self.assertEqual(
            response.data["asset_object"]["id"], str(self.assetbed.asset.external_id)
        )
        self.assertEqual(
            response.data["bed_object"]["id"], str(self.assetbed.bed.external_id)
        )

        invalid_updated_data = {
            "asset": self.asset3.external_id,
            "meta": {"sample_data": "sample value"},
        }
        response = self.client.put(
            self.get_url(external_id=self.assetbed.external_id),
            invalid_updated_data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        invalid_updated_data = {
            "bed": self.bed3.external_id,
            "meta": {"sample_data": "sample value"},
        }
        response = self.client.put(
            self.get_url(external_id=self.assetbed.external_id),
            invalid_updated_data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        updated_data = {
            "bed": self.bed4.external_id,
            "asset": self.asset1.external_id,
            "meta": {"sample_data": "sample value"},
        }
        response = self.client.put(
            self.get_url(external_id=self.assetbed.external_id),
            updated_data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assetbed.refresh_from_db()

        self.assertEqual(self.assetbed.bed.external_id, self.bed4.external_id)
        self.assertEqual(self.assetbed.asset.external_id, self.asset1.external_id)
        self.assertEqual(self.assetbed.meta, {"sample_data": "sample value"})

    def test_patch_assetbed(self):
        # checking old values
        response = self.client.get(self.get_url(external_id=self.assetbed.external_id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["meta"], {})
        self.assertEqual(
            response.data["asset_object"]["id"], str(self.assetbed.asset.external_id)
        )
        self.assertEqual(
            response.data["bed_object"]["id"], str(self.assetbed.bed.external_id)
        )

        invalid_updated_data = {
            "asset": self.asset3.external_id,
            "meta": {"sample_data": "sample value"},
        }
        response = self.client.patch(
            self.get_url(external_id=self.assetbed.external_id),
            invalid_updated_data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        invalid_updated_data = {
            "bed": self.bed4.external_id,
            "meta": {"sample_data": "sample value"},
        }
        response = self.client.patch(
            self.get_url(external_id=self.assetbed.external_id),
            invalid_updated_data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        updated_data = {
            "bed": self.bed4.external_id,
            "asset": self.asset1.external_id,
        }

        response = self.client.patch(
            self.get_url(external_id=self.assetbed.external_id),
            updated_data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assetbed.refresh_from_db()

        self.assertEqual(self.assetbed.bed.external_id, self.bed4.external_id)
        self.assertEqual(self.assetbed.asset.external_id, self.asset1.external_id)

    def test_delete_assetbed(self):
        # confirming that the object exist
        response = self.client.get(self.get_url(external_id=self.assetbed.external_id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.delete(
            self.get_url(external_id=self.assetbed.external_id)
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # confirming if it's deleted
        response = self.client.get(self.get_url(external_id=self.assetbed.external_id))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # confirming using db
        self.assetbed.refresh_from_db()
        self.assertFalse(
            AssetBed.objects.filter(external_id=self.assetbed.external_id).exists()
        )
