from unittest.mock import patch

from redis.exceptions import RedisError
from redis_om.model.model import NotFoundError as RedisModelNotFoundError
from rest_framework import status
from rest_framework.test import APITestCase

from care.facility.models import ICD11Diagnosis
from care.utils.tests.test_utils import TestUtils


class TestICD11Api(TestUtils, APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.state = cls.create_state()
        cls.district = cls.create_district(cls.state)
        cls.local_body = cls.create_local_body(cls.district)
        cls.super_user = cls.create_super_user("su", cls.district)
        cls.facility = cls.create_facility(cls.super_user, cls.district, cls.local_body)
        cls.user = cls.create_user(
            "icd11_doctor", cls.district, home_facility=cls.facility
        )

    def search_icd11(self, query):
        return self.client.get("/api/v1/icd/", {"query": query})

    def test_search_no_disease_code(self):
        res = self.search_icd11("14 Diseases of the skin")
        self.assertNotContains(res, "14 Diseases of the skin")

        res = self.search_icd11("Acute effects of ionizing radiation on the skin")
        self.assertNotContains(res, "Acute effects of ionizing radiation on the skin")

    def test_search_with_disease_code(self):
        res = self.search_icd11("aCuTe radiodermatitis following radiotherapy")
        self.assertContains(res, "EL60 Acute radiodermatitis following radiotherapy")

        res = self.search_icd11("cutaneous reactions")
        self.assertContains(res, "EK50.0 Cutaneous insect bite reactions")

        res = self.search_icd11("Haemorrhage rectum")
        self.assertContains(res, "ME24.A1 Haemorrhage of anus and rectum")

        res = self.search_icd11("ME24.A1")
        self.assertContains(res, "ME24.A1 Haemorrhage of anus and rectum")

        res = self.search_icd11("CA22.Z")
        self.assertContains(res, "CA22.Z Chronic obstructive pulmonary disease")

        res = self.search_icd11("1A00 Cholera")
        self.assertContains(res, "1A00 Cholera")

    def test_get_icd11_by_valid_id(self):
        res = self.client.get("/api/v1/icd/133207228/")
        self.assertEqual(
            res.data["label"], "CA22 Chronic obstructive pulmonary disease"
        )

    def test_get_icd11_by_invalid_id(self):
        res = self.client.get("/api/v1/icd/invalid/")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("ID must be an integer.", res.json())

        res = self.client.get("/api/v1/icd/0/")
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn(
            "Diagnosis with the specified ID not found.", res.json()["detail"]
        )

    @patch("care.facility.static_data.icd11.ICD11.get")
    def test_retrieve_diagnosis_not_found_in_redis_and_db(self, mock_redis_get):
        mock_redis_get.side_effect = RedisModelNotFoundError(
            "Diagnosis not found in Redis"
        )

        with patch.object(
            ICD11Diagnosis.objects, "get", side_effect=ICD11Diagnosis.DoesNotExist
        ):
            response = self.client.get("/api/v1/icd/123/")
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
            self.assertEqual(
                response.json()["detail"], "Diagnosis with the specified ID not found."
            )

    @patch("care.facility.static_data.icd11.ICD11.get")
    def test_retrieve_redis_connection_error(self, mock_redis_get):
        mock_redis_get.side_effect = RedisError("Redis connection issue")

        response = self.client.get("/api/v1/icd/123/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json()["detail"], "Redis connection issue encountered."
        )

    @patch("care.facility.static_data.icd11.ICD11.get")
    def test_retrieve_unexpected_error(self, mock_redis_get):
        mock_redis_get.side_effect = Exception("Unexpected error")

        response = self.client.get("/api/v1/icd/123/")
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.json()["detail"], "Internal Server Error")
