from django.db import models

from care.camera_plugin.models.json_schema.position import CAMERA_PRESET_POSITION_SCHEMA
from care.facility.models import AssetBed
from care.users.models import User
from care.utils.models.base import BaseModel
from care.utils.models.validators import JSONFieldSchemaValidator


class CameraPositionPreset(BaseModel):
    name = models.CharField(max_length=255, null=True)
    asset_bed = models.ForeignKey(
        AssetBed, on_delete=models.PROTECT, related_name="camera_presets"
    )
    position = models.JSONField(
        validators=[JSONFieldSchemaValidator(CAMERA_PRESET_POSITION_SCHEMA)]
    )
    created_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.PROTECT, related_name="+"
    )
    updated_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.PROTECT, related_name="+"
    )
    is_migrated = models.BooleanField(default=False)
