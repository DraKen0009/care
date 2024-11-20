class AssetMetaRegistry:
    _registry = {}

    @classmethod
    def register_meta(cls, name, schema):
        """
        Register a schema for a specific asset class.
        """
        cls._registry[name] = schema

    @classmethod
    def get_meta(cls, name):
        """
        Retrieve a schema by name.
        """
        return cls._registry.get(name)

    @classmethod
    def all_metas(cls):
        """
        Retrieve all registered schemas.
        """
        return cls._registry


def get_dynamic_asset_meta():
    """
    Dynamically construct the ASSET_META schema to include registered plugin schemas.
    """
    return {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "anyOf": [
            {"$ref": "#/definitions/hl7monitor"},
            {"$ref": "#/definitions/ventilator"},
            {"$ref": "#/definitions/empty"},
            # Include all registered plugin schemas
            *[
                {"$ref": f"#/definitions/{key}"}
                for key in AssetMetaRegistry.all_metas()
            ],
        ],
        "definitions": {
            "hl7monitor": {
                "type": "object",
                "required": ["local_ip_address"],
                "properties": {
                    "local_ip_address": {"type": "string"},
                    "middleware_hostname": {"type": "string"},
                    "asset_type": {"type": "string"},
                    "insecure_connection": {"type": "boolean"},
                },
                "additionalProperties": False,
            },
            "ventilator": {
                "type": "object",
                "required": ["local_ip_address"],
                "properties": {
                    "local_ip_address": {"type": "string"},
                    "middleware_hostname": {"type": "string"},
                    "asset_type": {"type": "string"},
                    "insecure_connection": {"type": "boolean"},
                },
                "additionalProperties": False,
            },
            # Including plugin-specific schemas
            **AssetMetaRegistry.all_metas(),
            "empty": {"type": "object", "additionalProperties": False},
        },
    }
