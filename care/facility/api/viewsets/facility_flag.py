from rest_framework import viewsets

from care.facility.api.serializers.facility_flag import FacilityFlagSerializer
from care.facility.models import FacilityFlag
from care.utils.custom_permissions import IsSuperUser


class FacilityFlagViewSet(viewsets.ModelViewSet):
    queryset = FacilityFlag.objects.all()
    serializer_class = FacilityFlagSerializer
    permission_classes = [IsSuperUser]
    lookup_field = "external_id"
