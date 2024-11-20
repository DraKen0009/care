from plugs.manager import PlugManager
from plugs.plug import Plug

abdm_plugin = Plug(
    name="abdm",
    package_name="git+https://github.com/ohcnetwork/care_abdm.git",
    version="@main",
    configs={},
)

hcx_plugin = Plug(
    name="hcx",
    package_name="git+https://github.com/ohcnetwork/care_hcx.git",
    version="@main",
    configs={},
)

camera_plugin = Plug(
    name="camera", package_name="/app/camera_plugin", version="", configs={}
)

plugs = [hcx_plugin, abdm_plugin, camera_plugin]

manager = PlugManager(plugs)
