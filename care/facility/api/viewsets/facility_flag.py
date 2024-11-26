from django_filters import rest_framework as filters
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from care.facility.api.serializers.facility_flag import FacilityFlagSerializer
from care.facility.models import FacilityFlag
from care.utils.custom_permissions import IsSuperUser


class FacilityFlagFilter(filters.FilterSet):
    flag = filters.CharFilter(field_name="flag", lookup_expr="icontains")
    facility = filters.UUIDFilter(field_name="facility__external_id")


class FacilityFlagViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for FacilityFlag model.

    This viewset is restricted to superusers only and provides endpoints to manage facility flags.
    """

    queryset = FacilityFlag.objects.all()
    serializer_class = FacilityFlagSerializer
    permission_classes = [IsSuperUser]
    lookup_field = "external_id"

    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = FacilityFlagFilter

    @action(detail=False, methods=["get"], url_path="available-flags")
    def list_available_flags(self, request):
        """
        List all available flags for FacilityFlag.
        """
        flags = FacilityFlag.objects.values_list("flag", flat=True).distinct()
        return Response({"available_flags": list(flags)}, status=status.HTTP_200_OK)
