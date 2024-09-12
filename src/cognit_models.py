from pydantic import BaseModel, Field
from enum import Enum

DESCRIPTIONS = {
    'app_requirement': {
        'requirement': "Requirement that needs to be taken into account",
        'scheduling': "Scheduling policy that applies to the requirement"
    },
    'edge_cluster_fe': {
        'id': "Cluster ID in the Cloud Edge Manager cluster pool",
        'name': "Cluster name",
        'hosts': "Hypervisor nodes ID belonging to the cluster",
        'datastores': "Datastores ID belonging to the cluster",
        'vnets': "Virtual Networks ID belonging to the cluster",
        'template': "Additional misc information of the cluster"
    },
    'function': {
        'lang': "Programming Language of the function",
        'fc': "Function bytes serialized and encoded in base64",
        'fc_hash': "Function contents hash. Acts as a function ID."
    }
}


class AppRequirements(BaseModel):
    REQUIREMENT: str = Field(
        description=DESCRIPTIONS['app_requirement']['requirement'])
    SCHEDULING_POLICY: str = Field(
        description=DESCRIPTIONS['app_requirement']['scheduling'])


class EdgeClusterFrontend(BaseModel):
    ID: int = Field(description=DESCRIPTIONS['edge_cluster_fe']['id'])
    NAME: str = Field(description=DESCRIPTIONS['edge_cluster_fe']['name'])
    HOSTS: list[int] = Field(
        description=DESCRIPTIONS['edge_cluster_fe']['hosts'])
    DATASTORES: list[int] = Field(
        description=DESCRIPTIONS['edge_cluster_fe']['datastores'])
    VNETS: list[int] = Field(
        description=DESCRIPTIONS['edge_cluster_fe']['vnets'])
    TEMPLATE: dict = Field(
        description=DESCRIPTIONS['edge_cluster_fe']['template'])


class FunctionLanguage(str, Enum):
    PY = "PY"
    C = "C"


class ExecSyncParams(BaseModel):
    LANG: FunctionLanguage = Field(
        description=DESCRIPTIONS['function']['lang'])
    FC: str = Field(description=DESCRIPTIONS['function']['fc'])
    FC_HASH: str = Field(description=DESCRIPTIONS['function']['fc_hash'])
