from django.apps import AppConfig

from care.camera_plugin.utils.onvif import OnvifAsset
from care.utils.assetintegration.asset_classes import AssetClasses


class CameraPluginConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "care.camera_plugin"

    def ready(self):
        AssetClasses.register("ONVIF", OnvifAsset)
