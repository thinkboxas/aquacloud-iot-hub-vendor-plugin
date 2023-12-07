from asyncua import Node

from aquacloud_common.models.sensor.environment.oxygen_saturation_sensor import OxygenSaturationSensorModel
from core.opcua.nodes.analog_item_node import AnalogItemNode
from core.opcua.nodes.base_sensor_node import BaseSensorNode


class OxygenSaturationSensorNode(BaseSensorNode):
    def __init__(self, model: OxygenSaturationSensorModel, ns: int, parent_node: Node, path: str = ""):
        super().__init__(model, ns, parent_node, path)
        self.model = model

    async def update_analog_item_variables_node(self):
        oxygen_saturation = await self.node.get_child(str(self.ns) + ":" + "OxygenSaturation")
        if oxygen_saturation is not None:
            await AnalogItemNode(oxygen_saturation, self.model.oxygen_saturation).update_properties_node()
