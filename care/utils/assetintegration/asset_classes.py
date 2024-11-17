from care.utils.assetintegration.hl7monitor import HL7MonitorAsset
from care.utils.assetintegration.utils import MutableEnum
from care.utils.assetintegration.ventilator import VentilatorAsset


class AssetClasses(MutableEnum):
    pass


AssetClasses.register("HL7MONITOR", HL7MonitorAsset)
AssetClasses.register("VENTILATOR", VentilatorAsset)
