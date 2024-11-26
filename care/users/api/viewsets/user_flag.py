from django_filters import rest_framework as filters
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

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

    @action(detail=False, methods=["get"], url_path="available-flags")
    def list_available_flags(self, request):
        """
        List all available flags for FacilityFlag.
        """
        flags = UserFlag.objects.values_list("flag", flat=True).distinct()
        return Response({"available_flags": list(flags)}, status=status.HTTP_200_OK)
