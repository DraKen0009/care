import enum

from rest_framework.exceptions import ValidationError

from care.utils.assetintegration.base import ActionParams, BaseAssetIntegration


class VentilatorAsset(BaseAssetIntegration):
    _name = "ventilator"

    class VentilatorActions(enum.Enum):
        GET_VITALS = "get_vitals"
        GET_STREAM_TOKEN = "get_stream_token"

    def __init__(self, meta):
        try:
            super().__init__(meta)
        except KeyError as e:
            raise ValidationError(
                {key: f"{key} not found in asset metadata" for key in e.args}
            ) from e

    def handle_action(self, user, **kwargs: ActionParams):
        action_type = kwargs["type"]
        timeout = kwargs.get("timeout")

        if action_type == self.VentilatorActions.GET_VITALS.value:
            request_params = {"device_id": self.host}
            return self.api_get(self.get_url("vitals"), request_params, timeout)

        if action_type == self.VentilatorActions.GET_STREAM_TOKEN.value:
            return self.api_post(
                self.get_url("api/stream/getToken/vitals"),
                {
                    "asset_id": self.id,
                    "ip": self.host,
                },
                timeout,
            )

        raise ValidationError({"action": "invalid action type"})

    @classmethod
    def get_action_choices(cls):
        choices = []
        choices += [(e.value, e.name) for e in cls.VentilatorActions]
        return choices

    @staticmethod
    def is_movable():
        return True

    @staticmethod
    def can_be_linked_to_consultation_bed():
        return True

    @staticmethod
    def can_be_linked_to_asset_bed():
        return False

    def get_asset_status(self):
        return self.api_get(self.get_url("devices/status"))
