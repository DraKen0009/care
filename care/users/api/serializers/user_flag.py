from rest_framework import serializers

from care.users.models import User, UserFlag
from care.utils.serializers.fields import ExternalIdSerializerField


class UserFlagSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="external_id", read_only=True)
    user = ExternalIdSerializerField(queryset=User.objects.all(), required=True)

    class Meta:
        model = UserFlag
        exclude = ["external_id", "deleted", "modified_date"]
