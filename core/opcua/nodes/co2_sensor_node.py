from asyncua import Node

from aquacloud_common.models.sensor.environment.co2_sensor import CO2SensorModel
from core.opcua.nodes.analog_item_node import AnalogItemNode
from core.opcua.nodes.base_sensor_node import BaseSensorNode


class CO2SensorNode(BaseSensorNode):
    def __init__(self, model: CO2SensorModel, ns: int, parent_node: Node, path: str = ""):
        super().__init__(model, ns, parent_node, path)
        self.model = model

    async def update_analog_item_variables_node(self):
        co2 = await self.node.get_child(str(self.ns) + ":" + "CO2")
        if co2 is not None:
            await AnalogItemNode(co2, self.model.co2).update_properties_node()