from django.shortcuts import get_object_or_404
from rest_framework.exceptions import NotFound
from rest_framework.mixins import ListModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from care.camera_plugin.api.serializers.camera_position_preset import (
    CameraPositionPresetSerializer,
)
from care.camera_plugin.models.camera_position_preset import CameraPositionPreset
from care.utils.queryset.asset_bed import (
    get_asset_bed_queryset,
    get_asset_queryset,
    get_bed_queryset,
)


class AssetBedCameraPositionPresetViewSet(ModelViewSet):
    serializer_class = CameraPositionPresetSerializer
    queryset = CameraPositionPreset.objects.all().select_related(
        "asset_bed", "created_by", "updated_by"
    )
    lookup_field = "external_id"
    permission_classes = (IsAuthenticated,)

    def get_asset_bed_obj(self):
        queryset = get_asset_bed_queryset(self.request.user).filter(
            external_id=self.kwargs["assetbed_external_id"]
        )
        return get_object_or_404(queryset)

    def get_queryset(self):
        return super().get_queryset().filter(asset_bed=self.get_asset_bed_obj())

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["asset_bed"] = self.get_asset_bed_obj()
        return context


class CameraPresetPositionViewSet(GenericViewSet, ListModelMixin):
    serializer_class = CameraPositionPresetSerializer
    queryset = CameraPositionPreset.objects.all().select_related(
        "asset_bed", "created_by", "updated_by"
    )
    lookup_field = "external_id"
    permission_classes = (IsAuthenticated,)

    def get_bed_obj(self, external_id: str):
        queryset = get_bed_queryset(self.request.user).filter(external_id=external_id)
        return get_object_or_404(queryset)

    def get_asset_obj(self, external_id: str):
        queryset = get_asset_queryset(self.request.user).filter(external_id=external_id)
        return get_object_or_404(queryset)

    def get_queryset(self):
        queryset = super().get_queryset()
        if asset_external_id := self.kwargs.get("asset_external_id"):
            return queryset.filter(
                asset_bed__asset=self.get_asset_obj(asset_external_id)
            )
        if bed_external_id := self.kwargs.get("bed_external_id"):
            return queryset.filter(asset_bed__bed=self.get_bed_obj(bed_external_id))
        raise NotFound
