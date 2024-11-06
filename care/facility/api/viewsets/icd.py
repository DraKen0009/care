from redis_om import FindQuery
from rest_framework.exceptions import APIException, NotFound, ValidationError
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from care.facility.static_data.icd11 import ICD11, get_icd11_diagnosis_object_by_id
from care.utils.exceptions import ICD11DiagnosisNotFoundError, ICD11RedisConnectionError
from care.utils.static_data.helpers import query_builder


class ICDViewSet(ViewSet):
    def serialize_data(self, objects: list[ICD11]):
        return [diagnosis.get_representation() for diagnosis in objects]

    def retrieve(self, request, pk: int):
        try:
            pk = int(pk)
        except ValueError as err:
            raise ValidationError(detail="ID must be an integer.") from err

        try:
            diagnosis = get_icd11_diagnosis_object_by_id(pk, as_dict=True)
            return Response(diagnosis)

        except ICD11DiagnosisNotFoundError as e:
            error_message = e.message
            raise NotFound(detail=error_message) from e

        except ICD11RedisConnectionError as e:
            error_message = e.message
            exception = APIException(error_message)
            exception.status_code = 400
            raise exception from e

        except Exception as e:
            error_message = "Internal Server Error"
            raise APIException(error_message) from e

    def list(self, request):
        try:
            limit = min(int(request.query_params.get("limit")), 20)
        except (ValueError, TypeError):
            limit = 20

        query = [
            ICD11.has_code == 1,
        ]
        if q := request.query_params.get("query"):
            query.append(ICD11.vec % query_builder(q))

        result = FindQuery(expressions=query, model=ICD11, limit=limit).execute(
            exhaust_results=False
        )
        return Response(self.serialize_data(result))
