from asyncua import Node

from aquacloud_common.models.sensor.environment.ftu_sensor import FTUSensorModel
from aquacloud_common.models.sensor.environment.light_sensor import LightSensorModel
from core.opcua.nodes.analog_item_node import AnalogItemNode
from core.opcua.nodes.base_sensor_node import BaseSensorNode


class LightSensorNode(BaseSensorNode):
    def __init__(self, model:  LightSensorModel, ns: int, parent_node: Node, path: str = ""):
        super().__init__(model, ns, parent_node, path)
        self.model = model

    async def update_analog_item_variables_node(self):
        lux = await self.node.get_child(str(self.ns) + ":" + "Lux")
        if lux is not None:
            await AnalogItemNode(lux, self.model.lux).update_properties_node()