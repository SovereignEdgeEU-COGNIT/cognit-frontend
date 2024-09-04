from pydantic import BaseModel

class Credentials(BaseModel):
    user: str
    password: str


class AppRequirements(BaseModel):
    requirement: str
    scheduling_policy: str


class EdgeClusterFrontend(BaseModel):
    id: int
    name: str
    hosts: list[int]
    datastores: list[int]
    vnets: list[int]
    template: dict
