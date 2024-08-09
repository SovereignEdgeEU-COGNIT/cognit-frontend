from fastapi import FastAPI, status, HTTPException, Header
from pydantic import BaseModel
from typing import Annotated
import uvicorn

import cognit_conf as api_conf
import cognit_auth as auth

conf = api_conf.load()
auth.ONE_XMLRPC = conf['one_xmlrpc']

app = FastAPI()

class Credentials(BaseModel):
    user: str
    password: str

class AppRequirements(BaseModel):
    requirement: str
    scheduling_policy: str

class EdgeClusterFrontend(BaseModel):
    ecf_id: int
    ip_address: str

class BiscuitToken(BaseModel):
    authority_block: str
    revocation_id: str
    signed_by: str

@app.post("/v1/authenticate", status_code=status.HTTP_201_CREATED)
async def authenticate(credentials: Credentials) -> BiscuitToken:
    if not auth.is_user_valid(credentials.user, credentials.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = auth.generate_biscuit(credentials.user)
    return token

@app.post("/v1/app_requirements", status_code=status.HTTP_200_OK)
async def app_req_upload(requirements: AppRequirements, header: Annotated[str | None, Header()] = None) -> int:
    app_req_id = 69
    return app_req_id


@app.put("/v1/app_requirements/{id}", status_code=status.HTTP_200_OK)
async def app_req_update(id: int, requirements: AppRequirements):
    pass


@app.get("/v1/app_requirements/{id}", status_code=status.HTTP_200_OK)
async def app_req_get(id: int) -> AppRequirements:
    app_req = AppRequirements()
    return app_req


@app.get("/v1/ec_fe", status_code=status.HTTP_200_OK)
async def edge_cluster_ip_get() -> str:
    ecf = EdgeClusterFrontend()
    return ecf.ip_address

if __name__ == "__main__":
    uvicorn.run("main:app", host=conf['host'], port=conf['port'], reload=True)
