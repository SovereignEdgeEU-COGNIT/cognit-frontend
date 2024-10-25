from pydantic import BaseModel, Field, field_validator
from enum import Enum
from typing import Optional

DESCRIPTIONS = {
    'app_requirement': {
        'latency': "Maximum latency in milliseconds",
        'exec_time': "Max execution time allowed for the function to execute",
        'energy': "Minimum energy renewable percentage",
        'flavour': "String describing the flavour of the Runtime. There is one identifier per DaaS and FaaS corresponding to the different use cases",
        'geolocation': "Scheduling policy that applies to the requirement"
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
    FLAVOUR: str = Field(
        default="Nature",
        description=DESCRIPTIONS['app_requirement']['latency'])
    MAX_LATENCY: Optional[int] = Field(
        default=10,
        description=DESCRIPTIONS['app_requirement']['latency'])
    MAX_FUNCTION_EXECUTION_TIME: Optional[float] = Field(
        default=1.0,
        description=DESCRIPTIONS['app_requirement']['exec_time'])
    MIN_ENERGY_RENEWABLE_USAGE: Optional[int] = Field(
        default=80,
        description=DESCRIPTIONS['app_requirement']['energy'])
    GEOLOCATION: Optional[str] = Field(
        default=None,
        description=DESCRIPTIONS['app_requirement']['geolocation'])

    @field_validator('GEOLOCATION')
    @classmethod
    def validate_geolocation(cls, v, info):
        max_latency = info.data.get('MAX_LATENCY')
        max_latency_default = cls.model_fields['MAX_LATENCY'].default

        if max_latency != max_latency_default and v is None:
            raise ValueError('GEOLOCATION is required when MAX_LATENCY is set')
        return v

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

    def __str__(self):
        return self.value


class ExecSyncParams(BaseModel):
    LANG: FunctionLanguage = Field(
        description=DESCRIPTIONS['function']['lang'])
    FC: str = Field(description=DESCRIPTIONS['function']['fc'])
    FC_HASH: str = Field(description=DESCRIPTIONS['function']['fc_hash'])

    class Config:
        use_enum_values = True
