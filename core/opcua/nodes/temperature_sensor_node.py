from asyncua import Node

from aquacloud_common.models.sensor.environment.temperature_sensor import TemperatureSensorModel
from core.opcua.nodes.analog_item_node import AnalogItemNode
from core.opcua.nodes.base_sensor_node import BaseSensorNode


class TemperatureSensorNode(BaseSensorNode):
    def __init__(self, model: TemperatureSensorModel, ns: int, parent_node: Node, path: str = ""):
        super().__init__(model, ns, parent_node, path)
        self.model = model

    async def update_analog_item_variables_node(self):
        temperature = await self.node.get_child(str(self.ns) + ":" + "Temperature")
        if temperature is not None:
            await AnalogItemNode(temperature, self.model.temperature).update_properties_node()
