from asyncua import Node, ua

from aquacloud_common.models.sensor.feeding.feed_type import FeedTypeModel
from core.opcua.nodes.analog_item_node import AnalogItemNode
from utilities.opcua import parse_range, parse_eu_information, update_external_references_node


class FeedTypeNode:
    def __init__(self, node: Node, model: FeedTypeModel):
        self._model: FeedTypeModel = model
        self._node: Node = node

    async def update_variables_node(self):
        identifier = self._node.nodeid.Identifier.__str__()
        variables = await self._node.get_variables()
        for v in variables:
            if v.nodeid.Identifier == (identifier + ".Manufacturer"):
                await v.set_value(ua.String(self._model.manufacturer))
            elif v.nodeid.Identifier == (identifier + ".ProductCode"):
                await v.set_value(ua.String(self._model.product_code))
            elif v.nodeid.Identifier == (identifier + ".PurchaseNumber"):
                await v.set_value(ua.String(self._model.purchase_number))

        ns = str(self._node.nodeid.NamespaceIndex)
        mass_per_pellet_node = await self._node.get_child(ns + ":" + "MassPerPellet")
        if mass_per_pellet_node is not None:
            await AnalogItemNode(mass_per_pellet_node, self._model.mass_per_pellet).update_properties_node()

        pellet_size_node = await self._node.get_child(ns + ":" + "PelletSize")
        if pellet_size_node is not None:
            await AnalogItemNode(pellet_size_node, self._model.pellet_size).update_properties_node()

            # Update ExternalReferences
            external_references_node = await self._node.get_child(ns + ":ExternalReferences")
            if external_references_node is not None:
                await update_external_references_node(
                    int(ns),
                    external_references_node,
                    self._model.external_references,
                    identifier
                )