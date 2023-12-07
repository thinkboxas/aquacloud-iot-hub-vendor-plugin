from asyncua import Node

from aquacloud_common.models.sensor.analog_item_model import AnalogItemModel
from utilities.opcua import parse_range, parse_eu_information


class AnalogItemNode:
    def __init__(self, node: Node, model: AnalogItemModel):
        self._model: AnalogItemModel = model
        self._node: Node = node

    async def update_properties_node(self):
        identifier = self._node.nodeid.Identifier.__str__()
        properties = await self._node.get_properties()
        for p in properties:
            if p.nodeid.Identifier == (identifier + ".EURange"):
                await p.set_value(parse_range(self._model.eu_range))
            elif p.nodeid.Identifier == (identifier + ".InstrumentRange"):
                await p.set_value(parse_range(self._model.instrument_range))
            elif p.nodeid.Identifier == (identifier + ".EngineeringUnits"):
                await p.set_value(parse_eu_information(self._model.engineering_units))
