from rest_framework import serializers

from care.facility.models import Facility, FacilityFlag
from care.utils.serializers.fields import ExternalIdSerializerField


class FacilityFlagSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="external_id", read_only=True)
    facility = ExternalIdSerializerField(queryset=Facility.objects.all(), required=True)

    class Meta:
        model = FacilityFlag
        exclude = ["external_id", "deleted", "modified_date"]
