from pydantic import BaseModel

class Credentials(BaseModel):
    user: str
    password: str


class AppRequirements(BaseModel):
    REQUIREMENT: str
    SCHEDULING_POLICY: str


class EdgeClusterFrontend(BaseModel):
    ID: int
    NAME: str
    HOSTS: list[int]
    DATASTORES: list[int]
    VNETS: list[int]
    TEMPLATE: dict
