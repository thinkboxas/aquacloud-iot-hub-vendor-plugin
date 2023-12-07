from asyncua import Node

from aquacloud_common.models.sensor.environment.ftu_sensor import FTUSensorModel
from aquacloud_common.models.sensor.environment.ph_sensor import PHSensorModel
from core.opcua.nodes.analog_item_node import AnalogItemNode
from core.opcua.nodes.base_sensor_node import BaseSensorNode


class PHSensorNode(BaseSensorNode):
    def __init__(self, model: PHSensorModel, ns: int, parent_node: Node, path: str = ""):
        super().__init__(model, ns, parent_node, path)
        self.model = model

    async def update_analog_item_variables_node(self):
        ph = await self.node.get_child(str(self.ns) + ":" + "pH")
        if ph is not None:
            await AnalogItemNode(ph, self.model.ph).update_properties_node()