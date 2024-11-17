CAMERA_PRESET_POSITION_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "x": {"type": "number"},
        "y": {"type": "number"},
        "zoom": {"type": "number"},
    },
    "required": ["x", "y", "zoom"],
    "additionalProperties": False,
}
