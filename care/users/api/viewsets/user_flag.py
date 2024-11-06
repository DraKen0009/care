from rest_framework import viewsets

from care.users.api.serializers.user_flag import UserFlagSerializer
from care.users.models import UserFlag
from care.utils.custom_permissions import IsSuperUser


class UserFlagViewSet(viewsets.ModelViewSet):
    queryset = UserFlag.objects.all()
    serializer_class = UserFlagSerializer
    permission_classes = [IsSuperUser]
    lookup_field = "external_id"
