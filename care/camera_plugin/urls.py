from django.urls import include, path
from rest_framework.routers import DefaultRouter

from care.camera_plugin.api.viewsets.camera_position_preset import (
    AssetBedCameraPositionPresetViewSet,
    CameraPresetPositionViewSet,
)
from config.api_router import (
    asset_nested_router,
    assetbed_nested_router,
    bed_nested_router,
)

camera_router = DefaultRouter()

asset_nested_router.register(
    r"camera_presets", CameraPresetPositionViewSet, basename="asset-camera-presets"
)
bed_nested_router.register(
    r"camera_presets", CameraPresetPositionViewSet, basename="bed-camera-presets"
)
assetbed_nested_router.register(
    r"camera_presets",
    AssetBedCameraPositionPresetViewSet,
    basename="assetbed-camera-presets",
)

# Include in urlpatterns
urlpatterns = [
    path("", include(asset_nested_router.urls)),
    path("", include(bed_nested_router.urls)),
    path("", include(assetbed_nested_router.urls)),
]
