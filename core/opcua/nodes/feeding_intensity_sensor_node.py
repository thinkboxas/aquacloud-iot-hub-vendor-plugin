from asyncua import Node

from aquacloud_common.models.sensor.feeding.feeding_intensity_sensor import FeedingIntensitySensorModel
from core.opcua.nodes.analog_item_node import AnalogItemNode
from core.opcua.nodes.base_sensor_node import BaseSensorNode


class FeedingIntensitySensorNode(BaseSensorNode):
    def __init__(self, model: FeedingIntensitySensorModel, ns: int, parent_node: Node, path: str = ""):
        super().__init__(model, ns, parent_node, path)
        self.model = model

    async def update_analog_item_variables_node(self):
        feeding_intensity = await self.node.get_child(str(self.ns) + ":" + "FeedingIntensity")
        if feeding_intensity is not None:
            await AnalogItemNode(feeding_intensity, self.model.feeding_intensity).update_properties_node()
