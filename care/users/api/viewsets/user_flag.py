from django_filters import rest_framework as filters
from rest_framework import viewsets

from care.users.api.serializers.user_flag import UserFlagSerializer
from care.users.models import UserFlag
from care.utils.custom_permissions import IsSuperUser


class UserFlagFilter(filters.FilterSet):
    flag = filters.CharFilter(field_name="flag", lookup_expr="icontains")
    user = filters.UUIDFilter(field_name="user__external_id")


class UserFlagViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for UserFlag model.

    This viewset is restricted to superusers only and provides endpoints to manage user flags.
    """

    queryset = UserFlag.objects.all()
    serializer_class = UserFlagSerializer
    permission_classes = [IsSuperUser]
    lookup_field = "external_id"

    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = UserFlagFilter
