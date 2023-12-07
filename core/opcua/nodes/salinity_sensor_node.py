from asyncua import Node

from aquacloud_common.models.sensor.environment.salinity_sensor import SalinitySensorModel
from core.opcua.nodes.analog_item_node import AnalogItemNode
from core.opcua.nodes.base_sensor_node import BaseSensorNode


class SalinitySensorNode(BaseSensorNode):
    def __init__(self, model: SalinitySensorModel, ns: int, parent_node: Node, path: str = ""):
        super().__init__(model, ns, parent_node, path)
        self.model = model

    async def update_analog_item_variables_node(self):
        salinity = await self.node.get_child(str(self.ns) + ":" + "Salinity")
        if salinity is not None:
            await AnalogItemNode(salinity, self.model.salinity).update_properties_node()
