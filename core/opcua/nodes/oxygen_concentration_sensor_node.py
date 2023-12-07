from asyncua import Node

from aquacloud_common.models.sensor.environment.oxygen_concentration_sensor import OxygenConcentrationSensorModel
from core.opcua.nodes.analog_item_node import AnalogItemNode
from core.opcua.nodes.base_sensor_node import BaseSensorNode


class OxygenConcentrationSensorNode(BaseSensorNode):
    def __init__(self, model: OxygenConcentrationSensorModel, ns: int, parent_node: Node, path: str = ""):
        super().__init__(model, ns, parent_node, path)
        self.model = model

    async def update_analog_item_variables_node(self):
        oxygen_concentration = await self.node.get_child(str(self.ns) + ":" + "OxygenConcentration")
        if oxygen_concentration is not None:
            await AnalogItemNode(oxygen_concentration, self.model.oxygen_concentration).update_properties_node()

        salinity = await self.node.get_child(str(self.ns) + ":" + "Salinity")
        if salinity is not None:
            await AnalogItemNode(salinity, self.model.salinity).update_properties_node()
