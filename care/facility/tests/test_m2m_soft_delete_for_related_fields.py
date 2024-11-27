from django.core.exceptions import ValidationError
from django.test import TestCase

from care.facility.models import (
    AssetLocation,
    Facility,
    FacilityDefaultAssetLocation,
    FacilityUser,
    InvestigationSession,
    InvestigationValue,
    PatientConsultation,
    PatientInvestigation,
    PatientInvestigationGroup,
    PatientRegistration,
    PatientSample,
    UserDefaultAssetLocation,
)
from care.users.models import User
from care.utils.tests.test_utils import TestUtils


class TestFacilityUserDeletion(TestUtils, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.state = cls.create_state()
        cls.district = cls.create_district(cls.state)
        cls.local_body = cls.create_local_body(cls.district)
        cls.super_user = cls.create_super_user("su", cls.district)

    def setUp(self):
        self.facility = self.create_facility(
            self.super_user, self.district, self.local_body
        )

        self.user1 = self.create_user(
            "user1",
            district=self.district,
            local_body=self.local_body,
        )
        self.user2 = self.create_user(
            "user2",
            district=self.district,
            local_body=self.local_body,
        )
        self.facility_user = self.create_facility_user(
            self.facility, self.user1, self.user2
        )

    def test_facility_user_delete_when_related_facility_is_deleted(self):
        self.assertTrue(FacilityUser.objects.filter(facility=self.facility).exists())

        self.facility.delete()
        self.assertFalse(FacilityUser.objects.filter(facility=self.facility).exists())

    def test_facility_user_delete_when_related_user_is_deleted(self):
        self.assertTrue(FacilityUser.objects.filter(user=self.user1).exists())

        self.user1.delete()

        self.assertFalse(
            User.objects.filter(external_id=self.user1.external_id).exists()
        )

    def test_facility_user_delete_when_related_created_by_is_deleted_for_existing_facility_user(
        self,
    ):
        # case 1 when facility user exist for create_by user
        self.assertTrue(FacilityUser.objects.filter(created_by=self.user2).exists())

        with self.assertRaises(ValidationError) as context:
            self.user2.delete()

        self.assertIn(
            f"Cannot delete User {self.user2} because they are referenced as `created_by` in FacilityUser records.",
            context.exception,
        )

        self.assertTrue(
            User.objects.filter(external_id=self.user2.external_id).exists()
        )

    def test_facility_user_delete_when_related_created_by_is_deleted(self):
        # case 2 when facility user doesn't exist for create_by user

        self.assertTrue(FacilityUser.objects.filter(created_by=self.user2).exists())
        FacilityUser.objects.filter(created_by=self.user2).delete()

        self.user2.delete()

        self.assertFalse(
            User.objects.filter(external_id=self.user2.external_id).exists()
        )


class TestInvestigationValueDeletion(TestUtils, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.state = cls.create_state()
        cls.district = cls.create_district(cls.state)
        cls.local_body = cls.create_local_body(cls.district)
        cls.super_user = cls.create_super_user("superuser", cls.district)
        cls.facility = cls.create_facility(cls.super_user, cls.district, cls.local_body)

    def setUp(self):
        # Create base objects for use in tests
        self.patient = self.create_patient(
            self.district, self.facility, local_body=self.local_body
        )
        self.consultation = self.create_consultation(self.patient, self.facility)
        self.investigation_group = self.create_investigation_group()
        self.investigation_session = self.create_patient_investigation_session(
            self.super_user
        )
        self.investigation = self.create_patient_investigation(self.investigation_group)

    def test_delete_patient_investigation_with_investigation_value(self):
        # Create an InvestigationValue referencing the PatientInvestigation
        InvestigationValue.objects.create(
            investigation=self.investigation,
            group=self.investigation_group,
            consultation=self.consultation,
            session=self.investigation_session,
        )

        # Attempt to delete the investigation
        with self.assertRaises(ValidationError) as context:
            self.investigation.delete()

        self.assertIn(
            f"Cannot delete PatientInvestigation {self.investigation!s} because they are referenced as `investigation` in InvestigationValue records.",
            context.exception,
        )

        # Ensure the investigation still exists
        self.assertTrue(
            PatientInvestigation.objects.filter(pk=self.investigation.pk).exists()
        )

    def test_delete_patient_investigation_without_investigation_value(self):
        # Ensure no InvestigationValue exists
        InvestigationValue.objects.filter(investigation=self.investigation).delete()

        # Delete the investigation
        self.investigation.delete()

        # Ensure the investigation is deleted
        self.assertFalse(
            PatientInvestigation.objects.filter(pk=self.investigation.pk).exists()
        )

    def test_delete_investigation_session_with_investigation_value(self):
        # Create an InvestigationValue referencing the InvestigationSession
        InvestigationValue.objects.create(
            investigation=self.investigation,
            group=self.investigation_group,
            consultation=self.consultation,
            session=self.investigation_session,
        )

        # Attempt to delete the session
        with self.assertRaises(ValidationError) as context:
            self.investigation_session.delete()

        self.assertIn(
            f"Cannot delete InvestigationSession {self.investigation_session.external_id} because they are referenced as `session` in InvestigationValue records.",
            str(context.exception),
        )

        # Ensure the session still exists
        self.assertTrue(
            InvestigationSession.objects.filter(
                pk=self.investigation_session.pk
            ).exists()
        )

    def test_delete_investigation_session_without_investigation_value(self):
        # Ensure no InvestigationValue exists
        InvestigationValue.objects.filter(session=self.investigation_session).delete()

        # Delete the session
        self.investigation_session.delete()

        # Ensure the session is deleted
        self.assertFalse(
            InvestigationSession.objects.filter(
                pk=self.investigation_session.pk
            ).exists()
        )

    def test_delete_patient_investigation_group_with_investigation_value(self):
        # Create an InvestigationValue referencing the PatientInvestigationGroup
        InvestigationValue.objects.create(
            investigation=self.investigation,
            group=self.investigation_group,
            consultation=self.consultation,
            session=self.investigation_session,
        )

        # Attempt to delete the group
        with self.assertRaises(ValidationError) as context:
            self.investigation_group.delete()

        self.assertIn(
            f"Cannot delete PatientInvestigationGroup {self.investigation_group.name} because they are referenced as `group` in InvestigationValue records.",
            str(context.exception),
        )

        # Ensure the group still exists
        self.assertTrue(
            PatientInvestigationGroup.objects.filter(
                pk=self.investigation_group.pk
            ).exists()
        )

    def test_delete_patient_investigation_group_without_investigation_value(self):
        # Ensure no InvestigationValue exists
        InvestigationValue.objects.filter(group=self.investigation_group).delete()

        # Delete the group
        self.investigation_group.delete()

        # Ensure the group is deleted
        self.assertFalse(
            PatientInvestigationGroup.objects.filter(
                pk=self.investigation_group.pk
            ).exists()
        )

    def test_delete_patient_consultation_with_investigation_value(self):
        # Create an InvestigationValue referencing the PatientConsultation
        InvestigationValue.objects.create(
            investigation=self.investigation,
            group=self.investigation_group,
            consultation=self.consultation,
            session=self.investigation_session,
        )

        # Attempt to delete the consultation
        with self.assertRaises(ValidationError) as context:
            self.consultation.delete()

        self.assertIn(
            f"Cannot delete PatientConsultation {self.consultation.external_id} because they are referenced as `consultation` in InvestigationValue records.",
            str(context.exception),
        )

        # Ensure the consultation still exists
        self.assertTrue(
            PatientConsultation.objects.filter(pk=self.consultation.pk).exists()
        )

    def test_delete_patient_consultation_without_investigation_value(self):
        # Ensure no InvestigationValue exists
        InvestigationValue.objects.filter(consultation=self.consultation).delete()

        # Delete the consultation
        self.consultation.delete()

        # Ensure the consultation is deleted
        self.assertFalse(
            PatientConsultation.objects.filter(pk=self.consultation.pk).exists()
        )


class TestPatientSampleDeletion(TestUtils, TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create necessary related objects
        cls.state = cls.create_state()
        cls.district = cls.create_district(cls.state)
        cls.local_body = cls.create_local_body(cls.district)
        cls.super_user = cls.create_super_user("superuser", cls.district)
        cls.facility = cls.create_facility(cls.super_user, cls.district, cls.local_body)

    def setUp(self):
        # Create patient and consultation for the tests
        self.patient = self.create_patient(self.district, self.facility)
        self.consultation = self.create_consultation(self.patient, self.facility)

        # Create a user to act as the creator
        self.user = self.create_user("test_user", district=self.district)

        # Create a sample linked to the patient and consultation
        self.sample = self.create_patient_sample(
            self.patient, self.consultation, self.facility, self.user
        )

    def test_delete_patient_registration_with_related_sample(self):
        # Ensure the sample is linked to the patient
        self.assertTrue(PatientSample.objects.filter(patient=self.patient).exists())

        # Attempt to delete the patient
        with self.assertRaises(ValidationError) as context:
            self.patient.delete()

        self.assertIn(
            f"Cannot delete PatientRegistration {self.patient} because they are referenced as `patient` in PatientSample records.",
            str(context.exception),
        )

        # Ensure the patient and sample still exist
        self.assertTrue(PatientRegistration.objects.filter(pk=self.patient.pk).exists())
        self.assertTrue(PatientSample.objects.filter(pk=self.sample.pk).exists())

    def test_delete_patient_registration_without_sample(self):
        # Delete the sample first
        self.sample.delete()

        # Ensure the sample no longer exists
        self.assertFalse(PatientSample.objects.filter(patient=self.patient).exists())

        # Now delete the patient
        self.patient.delete()

        # Ensure the patient is deleted
        self.assertFalse(
            PatientRegistration.objects.filter(pk=self.patient.pk).exists()
        )

    def test_delete_patient_consultation_with_related_sample(self):
        # Ensure the sample is linked to the consultation
        self.assertTrue(
            PatientSample.objects.filter(consultation=self.consultation).exists()
        )

        # Attempt to delete the consultation
        with self.assertRaises(ValidationError) as context:
            self.consultation.delete()

        self.assertIn(
            f"Cannot delete PatientConsultation {self.consultation} because they are referenced as `consultation` in PatientSample records.",
            str(context.exception),
        )

        # Ensure the consultation and sample still exist
        self.assertTrue(
            PatientConsultation.objects.filter(pk=self.consultation.pk).exists()
        )
        self.assertTrue(PatientSample.objects.filter(pk=self.sample.pk).exists())

    def test_delete_patient_consultation_without_sample(self):
        # Delete the sample first
        self.sample.delete()

        # Ensure the sample no longer exists
        self.assertFalse(
            PatientSample.objects.filter(consultation=self.consultation).exists()
        )

        # Now delete the consultation
        self.consultation.delete()

        # Ensure the consultation is deleted
        self.assertFalse(
            PatientConsultation.objects.filter(pk=self.consultation.pk).exists()
        )

    def test_delete_patient_sample(self):
        # Ensure the sample exists
        self.assertTrue(PatientSample.objects.filter(pk=self.sample.pk).exists())

        # Delete the sample
        self.sample.delete()

        # Ensure the sample is deleted
        self.assertFalse(PatientSample.objects.filter(pk=self.sample.pk).exists())

    def test_delete_created_by_user_sets_null_in_patient_sample(self):
        # Ensure the created_by user is linked to the sample
        self.assertEqual(self.sample.created_by, self.user)

        # Delete the user
        self.user.delete()

        # Reload the sample and ensure `created_by` is now NULL
        self.sample.refresh_from_db()
        self.assertIsNone(self.sample.created_by)

    def test_delete_last_edited_by_user_sets_null_in_patient_sample(self):
        # Ensure the last_edited_by user is linked to the sample
        self.assertEqual(self.sample.last_edited_by, self.user)

        # Delete the user
        self.user.delete()

        # Reload the sample and ensure `last_edited_by` is now NULL
        self.sample.refresh_from_db()
        self.assertIsNone(self.sample.last_edited_by)

    def test_delete_created_by_and_last_edited_by_users_sets_null_in_patient_sample(
        self,
    ):
        # Ensure the created_by and last_edited_by users are linked to the sample
        self.assertEqual(self.sample.created_by, self.user)
        self.assertEqual(self.sample.last_edited_by, self.user)

        # Delete the user
        self.user.delete()

        # Reload the sample and ensure both fields are now NULL
        self.sample.refresh_from_db()
        self.assertIsNone(self.sample.created_by)
        self.assertIsNone(self.sample.last_edited_by)

    def test_delete_user_sets_null_in_multiple_samples(self):
        # Create another sample by the same user
        sample2 = PatientSample.objects.create(
            patient=self.patient,
            consultation=self.consultation,
            sample_type=0,
            created_by=self.user,
            last_edited_by=self.user,
        )

        # Ensure the user is linked to both samples
        self.assertEqual(self.sample.created_by, self.user)
        self.assertEqual(self.sample.last_edited_by, self.user)
        self.assertEqual(sample2.created_by, self.user)
        self.assertEqual(sample2.last_edited_by, self.user)

        # Delete the user
        self.user.delete()

        # Reload both samples and ensure both fields are now NULL
        self.sample.refresh_from_db()
        sample2.refresh_from_db()
        self.assertIsNone(self.sample.created_by)
        self.assertIsNone(self.sample.last_edited_by)
        self.assertIsNone(sample2.created_by)
        self.assertIsNone(sample2.last_edited_by)


class TestUserDefaultAssetLocation(TestUtils, TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create necessary data
        cls.state = cls.create_state()
        cls.district = cls.create_district(cls.state)
        cls.super_user = cls.create_super_user("superuser", cls.district)
        cls.local_body = cls.create_local_body(cls.district)
        cls.facility = cls.create_facility(cls.super_user, cls.district, cls.local_body)

    def setUp(self):
        # Create a user and a UserDefaultAssetLocation
        self.user = self.create_user("test_user", district=self.district)
        self.location = self.create_asset_location(self.facility)
        self.user_default_location = self.create_user_default_asset_location(
            user=self.user, location=self.location
        )

    def test_delete_user_with_related_user_default_asset_location(self):
        # Ensure the user is linked to UserDefaultAssetLocation
        self.assertTrue(
            UserDefaultAssetLocation.objects.filter(user=self.user).exists()
        )

        # Attempt to delete the user
        with self.assertRaises(ValidationError) as context:
            self.user.delete()

        # Assert that the exception is raised
        self.assertIn(
            f"Cannot delete User {self.user} because they are referenced as `user` in UserDefaultAssetLocation records.",
            str(context.exception),
        )

        # Ensure the user and UserDefaultAssetLocation still exist
        self.assertTrue(User.objects.filter(pk=self.user.pk).exists())
        self.assertTrue(
            UserDefaultAssetLocation.objects.filter(
                pk=self.user_default_location.pk
            ).exists()
        )

    def test_delete_location_with_related_user_default_asset_location(self):
        # Ensure the location is linked to UserDefaultAssetLocation
        self.assertTrue(
            UserDefaultAssetLocation.objects.filter(location=self.location).exists()
        )

        # Attempt to delete the location
        with self.assertRaises(ValidationError) as context:
            self.location.delete()

        # Assert that the correct exception is raised
        self.assertIn(
            f"Cannot delete AssetLocation {self.location} because they are referenced as `location` in UserDefaultAssetLocation records.",
            str(context.exception),
        )

        # Ensure the location and UserDefaultAssetLocation still exist
        self.assertTrue(AssetLocation.objects.filter(pk=self.location.pk).exists())
        self.assertTrue(
            UserDefaultAssetLocation.objects.filter(
                pk=self.user_default_location.pk
            ).exists()
        )

    def test_delete_user_default_asset_location(self):
        # Ensure the UserDefaultAssetLocation exists
        self.assertTrue(
            UserDefaultAssetLocation.objects.filter(
                pk=self.user_default_location.pk
            ).exists()
        )

        # Delete the UserDefaultAssetLocation
        self.user_default_location.delete()

        # Ensure it is deleted and other related objects are unaffected
        self.assertFalse(
            UserDefaultAssetLocation.objects.filter(
                pk=self.user_default_location.pk
            ).exists()
        )
        self.assertTrue(User.objects.filter(pk=self.user.pk).exists())
        self.assertTrue(AssetLocation.objects.filter(pk=self.location.pk).exists())

    def test_delete_user_default_asset_location_then_user(self):
        # Ensure the UserDefaultAssetLocation exists
        self.assertTrue(
            UserDefaultAssetLocation.objects.filter(
                pk=self.user_default_location.pk
            ).exists()
        )

        # Delete the UserDefaultAssetLocation
        self.user_default_location.delete()

        # Ensure it is deleted
        self.assertFalse(
            UserDefaultAssetLocation.objects.filter(
                pk=self.user_default_location.pk
            ).exists()
        )

        # Attempt to delete the User
        self.user.delete()

        # Ensure the User is deleted
        self.assertFalse(User.objects.filter(pk=self.user.pk).exists())

    def test_delete_user_default_asset_location_then_location(self):
        # Ensure the UserDefaultAssetLocation exists
        self.assertTrue(
            UserDefaultAssetLocation.objects.filter(
                pk=self.user_default_location.pk
            ).exists()
        )

        # Delete the UserDefaultAssetLocation
        self.user_default_location.delete()

        # Ensure it is deleted
        self.assertFalse(
            UserDefaultAssetLocation.objects.filter(
                pk=self.user_default_location.pk
            ).exists()
        )

        # Attempt to delete the Location
        self.location.delete()

        # Ensure the Location is deleted
        self.assertFalse(AssetLocation.objects.filter(pk=self.location.pk).exists())


class TestFacilityDefaultAssetLocation(TestUtils, TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create necessary data
        cls.state = cls.create_state()
        cls.district = cls.create_district(cls.state)
        cls.local_body = cls.create_local_body(cls.district)
        cls.super_user = cls.create_super_user("superuser", cls.district)
        cls.facility = cls.create_facility(cls.super_user, cls.district, cls.local_body)

    def setUp(self):
        # Create a location and a FacilityDefaultAssetLocation
        self.location = self.create_asset_location(self.facility)
        self.facility_default_location = self.create_facility_default_asset_location(
            facility=self.facility, location=self.location
        )

    def test_delete_facility_with_related_facility_default_asset_location(self):
        # Ensure the facility is linked to FacilityDefaultAssetLocation
        self.assertTrue(
            FacilityDefaultAssetLocation.objects.filter(facility=self.facility).exists()
        )

        # Attempt to delete the facility
        with self.assertRaises(ValidationError) as context:
            self.facility.delete()

        # Assert that the correct exception is raised
        self.assertIn(
            f"Cannot delete Facility {self.facility} because they are referenced as `facility` in FacilityDefaultAssetLocation records.",
            str(context.exception),
        )

        # Ensure the facility and FacilityDefaultAssetLocation still exist
        self.assertTrue(Facility.objects.filter(pk=self.facility.pk).exists())
        self.assertTrue(
            FacilityDefaultAssetLocation.objects.filter(
                pk=self.facility_default_location.pk
            ).exists()
        )

    def test_delete_location_with_related_facility_default_asset_location(self):
        # Ensure the location is linked to FacilityDefaultAssetLocation
        self.assertTrue(
            FacilityDefaultAssetLocation.objects.filter(location=self.location).exists()
        )

        # Attempt to delete the location
        with self.assertRaises(ValidationError) as context:
            self.location.delete()

        # Assert that the correct exception is raised
        self.assertIn(
            f"Cannot delete AssetLocation {self.location} because they are referenced as `location` in FacilityDefaultAssetLocation records.",
            str(context.exception),
        )

        # Ensure the location and FacilityDefaultAssetLocation still exist
        self.assertTrue(AssetLocation.objects.filter(pk=self.location.pk).exists())
        self.assertTrue(
            FacilityDefaultAssetLocation.objects.filter(
                pk=self.facility_default_location.pk
            ).exists()
        )

    def test_delete_facility_default_asset_location(self):
        # Ensure the FacilityDefaultAssetLocation exists
        self.assertTrue(
            FacilityDefaultAssetLocation.objects.filter(
                pk=self.facility_default_location.pk
            ).exists()
        )

        # Delete the FacilityDefaultAssetLocation
        self.facility_default_location.delete()

        # Ensure it is deleted and other related objects are unaffected
        self.assertFalse(
            FacilityDefaultAssetLocation.objects.filter(
                pk=self.facility_default_location.pk
            ).exists()
        )
        self.assertTrue(Facility.objects.filter(pk=self.facility.pk).exists())
        self.assertTrue(AssetLocation.objects.filter(pk=self.location.pk).exists())

    def test_delete_facility_default_asset_location_then_facility(self):
        # Ensure the FacilityDefaultAssetLocation exists
        self.assertTrue(
            FacilityDefaultAssetLocation.objects.filter(
                pk=self.facility_default_location.pk
            ).exists()
        )

        # Delete the FacilityDefaultAssetLocation
        self.facility_default_location.delete()

        # Ensure it is deleted
        self.assertFalse(
            FacilityDefaultAssetLocation.objects.filter(
                pk=self.facility_default_location.pk
            ).exists()
        )

        # Attempt to delete the Facility
        self.facility.delete()

        # Ensure the Facility is deleted
        self.assertFalse(Facility.objects.filter(pk=self.facility.pk).exists())

    def test_delete_facility_default_asset_location_then_location(self):
        # Ensure the FacilityDefaultAssetLocation exists
        self.assertTrue(
            FacilityDefaultAssetLocation.objects.filter(
                pk=self.facility_default_location.pk
            ).exists()
        )

        # Delete the FacilityDefaultAssetLocation
        self.facility_default_location.delete()

        # Ensure it is deleted
        self.assertFalse(
            FacilityDefaultAssetLocation.objects.filter(
                pk=self.facility_default_location.pk
            ).exists()
        )

        # Attempt to delete the Location
        self.location.delete()

        # Ensure the Location is deleted
        self.assertFalse(AssetLocation.objects.filter(pk=self.location.pk).exists())
