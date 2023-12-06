from asyncua import Node

from aquacloud_common.models.sensor.feeding.calculated_accumulated_feeding_sensor import \
    CalculatedAccumulatedFeedingSensorModel
from core.opcua.nodes.analog_item_node import AnalogItemNode
from core.opcua.nodes.base_sensor_node import BaseSensorNode


class CalculatedAccumulatedFeedingSensorNode(BaseSensorNode):
    def __init__(self, model: CalculatedAccumulatedFeedingSensorModel, ns: int, parent_node: Node, path: str = ""):
        super().__init__(model, ns, parent_node, path)
        self.model = model

    async def update_analog_item_variables_node(self):
        fed_amount = await self.node.get_child(str(self.ns) + ":" + "FedAmount")
        if fed_amount is not None:
            await AnalogItemNode(fed_amount, self.model.fed_amount).update_properties_node()
