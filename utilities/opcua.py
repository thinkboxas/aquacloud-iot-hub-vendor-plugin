from typing import Union

from asyncua import Node, ua

from aquacloud_common.core.core_type import OrgNodeType
from aquacloud_common.models.common.external_reference import ExternalReferenceModel
from aquacloud_common.models.common.position import PositionModel
from aquacloud_common.models.sensor.analog_item_model import Range, EUInformation
from core.opcua.nodes.external_reference_node import ExternalReference


async def update_external_references_node(
        ns: int,
        external_references_node: Node,
        external_references: list[ExternalReferenceModel],
        path: str = ""
):
    for external_reference in external_references:
        extr = ExternalReference(external_reference, ns, external_references_node, path)
        await extr.init()


async def update_position_node(
        ns: int,
        position_node: Node,
        position: PositionModel,
):
    # Update Properties
    namespace = str(ns)
    latitude = await position_node.get_child(namespace + ":Latitude")
    longitude = await position_node.get_child(namespace + ":Longitude")
    depth = await position_node.get_child(namespace + ":Depth")
    effective_range = await position_node.get_child(namespace + ":EffectiveRange")

    await latitude.set_value(ua.Float(position.latitude))
    await longitude.set_value(ua.Float(position.longitude))
    await depth.set_value(ua.Float(position.depth))
    await effective_range.set_value(ua.Float(position.effective_range))

    # Update External Reference
    external_references_node = await position_node.get_child(namespace + ":ExternalReferences")
    if external_references_node is not None:
        await update_external_references_node(
            ns, external_references_node,
            position.external_references,
            position_node.nodeid.Identifier.__str__()
        )


async def get_container_node_by_child_type(node: Node, child_type_definition: str) -> Node | None:
    try:
        type_definition_node = await node.read_type_definition()
        type_definition = type_definition_node.Identifier.__str__()
        ns = node.nodeid.NamespaceIndex
        if type_definition == OrgNodeType.GLOBAL:
            return await node.get_child(str(ns) + ":" + "Countries")
        elif type_definition == OrgNodeType.COUNTRY:
            return await node.get_child(str(ns) + ":" + "Regions")
        elif type_definition == OrgNodeType.REGION:
            return await node.get_child(str(ns) + ":" + "SubRegions")
        elif type_definition == OrgNodeType.SUB_REGION:
            if child_type_definition == OrgNodeType.SUB_REGION:
                return await node.get_child(str(ns) + ":" + "SubRegions")
            else:
                return await node.get_child(str(ns) + ":" + "Sites")
        elif type_definition == OrgNodeType.SITE:
            if child_type_definition == OrgNodeType.UNIT:
                return await node.get_child(str(ns) + ":" + "Units")
            else:
                return await node.get_child(str(ns) + ":" + "Sensors")
        elif type_definition == OrgNodeType.UNIT:
            return await node.get_child(str(ns) + ":" + "Sensors")
    except Exception as e:
        print(e)
        return None


async def get_node_containers(node: Node) -> list[Node]:
    containers = []
    try:
        type_definition_node = await node.read_type_definition()
        type_definition = type_definition_node.Identifier.__str__()
        ns = node.nodeid.NamespaceIndex
        if type_definition == OrgNodeType.GLOBAL:
            containers = [await node.get_child(str(ns) + ":" + "Countries"), node]
        elif type_definition == OrgNodeType.COUNTRY:
            containers = [await node.get_child(str(ns) + ":" + "Regions")]
        elif type_definition == OrgNodeType.REGION:
            containers = [await node.get_child(str(ns) + ":" + "SubRegions")]
        elif type_definition == OrgNodeType.SUB_REGION:
            sub_regions_node = await node.get_child(str(ns) + ":" + "SubRegions")
            sites_node = await node.get_child(str(ns) + ":" + "Sites")
            containers = [sub_regions_node, sites_node]
        elif type_definition == OrgNodeType.SITE:
            containers = [await node.get_child(str(ns) + ":" + "Units")]
        elif type_definition == OrgNodeType.UNIT:
            containers = [await node.get_child(str(ns) + ":" + "Sensors")]
    except Exception as e:
        print(e)

    return containers


def parse_range(r: Range) -> ua.Range:
    return ua.Range(Low=ua.Double(r.low), High=ua.Double(r.high))


def parse_eu_information(eu_information: EUInformation) -> ua.EUInformation:
    return ua.EUInformation(
        NamespaceUri=ua.String(eu_information.namespace_uri),
        UnitId=ua.Int32(eu_information.unit_id),
        DisplayName=ua.LocalizedText(eu_information.display_name),
        Description=ua.LocalizedText(eu_information.description)
    )
