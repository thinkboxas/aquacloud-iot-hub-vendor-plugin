from asyncua import Node

from aquacloud_common.core.core_type import OrgType
from aquacloud_common.models.common.aqua_base_model import AquaBaseModel
from aquacloud_common.models.organization.unit import UnitModel
from aquacloud_common.models.organization.country import CountryModel
from aquacloud_common.models.organization.global_model import GlobalModel
from aquacloud_common.models.organization.organization import OrganizationModel
from aquacloud_common.models.organization.region import RegionModel
from aquacloud_common.models.organization.site import SiteModel
from aquacloud_common.models.organization.sub_region import SubRegionModel


TYPE_DEFINITION_IDENTIFIER_PREFIX = "AquaCloud"


def parse_org_structure(org_tree: dict, org_type: str) -> OrganizationModel | None:
    if org_type == OrgType.GLOBAL:
        return GlobalModel.model_validate(org_tree)
    elif org_type == OrgType.COUNTRY:
        return CountryModel.model_validate(org_tree)
    elif org_type == OrgType.REGION:
        return RegionModel.model_validate(org_tree)
    elif org_type == OrgType.SUB_REGION:
        return SubRegionModel.model_validate(org_tree)
    elif org_type == OrgType.SITE:
        return SiteModel.model_validate(org_tree)
    elif org_type == OrgType.UNIT:
        return UnitModel.model_validate(org_tree)

    return None


def get_type_definition_identifier_from_model(model: AquaBaseModel) -> str:
    name = model.__class__.__name__
    return TYPE_DEFINITION_IDENTIFIER_PREFIX + "|" + name.replace("Model", "") + "Type"


def get_identifier_from_model(model: AquaBaseModel, parent_node: Node) -> str:
    name = model.__class__.__name__
    path = name.replace("Model", "") + "|" + model.name
    if parent_node is None:
        return name.replace("Model", "") + "|" + model.name
    else:
        return parent_node.nodeid.Identifier + "|" + path
