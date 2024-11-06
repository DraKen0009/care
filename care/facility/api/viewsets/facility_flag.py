from django_filters import rest_framework as filters
from rest_framework import viewsets

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
