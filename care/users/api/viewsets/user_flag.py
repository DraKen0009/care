from django_filters import rest_framework as filters
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from care.users.api.serializers.user_flag import UserFlagSerializer
from care.users.models import UserFlag
from care.utils.custom_permissions import IsSuperUser
from care.utils.registries.feature_flag import FlagRegistry, FlagType


class UserFlagFilter(filters.FilterSet):
    flag = filters.CharFilter(field_name="flag", lookup_expr="exact")
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
        try:
            flags = FlagRegistry.get_all_flags(FlagType.USER)
            return Response({"available_flags": list(flags)})
        except Exception as e:
            return Response(
                {"error": "Failed to fetch available flags", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
