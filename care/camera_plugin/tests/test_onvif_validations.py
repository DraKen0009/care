from care.camera_plugin.utils.onvif import OnvifAsset


def test_meta_validations_for_onvif_asset(self):
    valid_meta = {
        "local_ip_address": "192.168.0.1",
        "camera_access_key": "username:password:access_key",
        "middleware_hostname": "middleware.local",
        "insecure_connection": True,
    }
    onvif_asset = OnvifAsset(valid_meta)
    self.assertEqual(onvif_asset.middleware_hostname, "middleware.local")
    self.assertEqual(onvif_asset.host, "192.168.0.1")
    self.assertEqual(onvif_asset.username, "username")
    self.assertEqual(onvif_asset.password, "password")
    self.assertEqual(onvif_asset.access_key, "access_key")
    self.assertTrue(onvif_asset.insecure_connection)

    invalid_meta_cases = [
        # Invalid format for camera_access_key
        {
            "id": "123",
            "local_ip_address": "192.168.0.1",
            "middleware_hostname": "middleware.local",
            "camera_access_key": "invalid_format",
        },
        # Missing username/password in camera_access_key
        {
            "local_ip_address": "192.168.0.1",
            "middleware_hostname": "middleware.local",
            "camera_access_key": "invalid_format",
        },
        # Missing middleware_hostname
        {
            "local_ip_address": "192.168.0.1",
            "camera_access_key": "username:password:access_key",
        },
        # Missing local_ip_address
        {
            "middleware_hostname": "middleware.local",
            "camera_access_key": "username:password:access_key",
        },
        # Invalid value for insecure_connection
        {
            "local_ip_address": "192.168.0.1",
            "camera_access_key": "username:password:access_key",
            "middleware_hostname": "middleware.local",
            "insecure_connection": "invalid_value",
        },
    ]
    for meta in invalid_meta_cases:
        self.validate_invalid_meta(OnvifAsset, meta)
