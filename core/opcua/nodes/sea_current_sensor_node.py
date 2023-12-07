from asyncua import Node

from aquacloud_common.models.sensor.environment.sea_current_sensor import SeaCurrentSensorModel
from core.opcua.nodes.analog_item_node import AnalogItemNode
from core.opcua.nodes.base_sensor_node import BaseSensorNode


class SeaCurrentSensorNode(BaseSensorNode):
    def __init__(self, model: SeaCurrentSensorModel, ns: int, parent_node: Node, path: str = ""):
        super().__init__(model, ns, parent_node, path)
        self.model = model

    async def update_analog_item_variables_node(self):
        direction = await self.node.get_child(str(self.ns) + ":" + "Direction")
        if direction is not None:
            await AnalogItemNode(direction, self.model.direction).update_properties_node()

        speed = await self.node.get_child(str(self.ns) + ":" + "Speed")
        if speed is not None:
            await AnalogItemNode(speed, self.model.speed).update_properties_node()
