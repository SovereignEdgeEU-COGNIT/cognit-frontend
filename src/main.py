#!/usr/bin/env python

from fastapi import FastAPI, status, HTTPException, Header
from pydantic import BaseModel
from typing import Annotated
import uvicorn

import cognit_conf as conf
import cognit_auth as auth


class Credentials(BaseModel):
    user: str
    password: str


class AppRequirements(BaseModel):
    requirement: str
    scheduling_policy: str


auth.ONE_XMLRPC = conf.ONE_XMLRPC

app = FastAPI()


@app.post("/v1/authenticate", status_code=status.HTTP_201_CREATED)
async def authenticate(credentials: Credentials) -> str:
    if not auth.is_user_valid(credentials.user, credentials.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = auth.generate_biscuit(credentials.user)
    return token


@app.post("/v1/app_requirements", status_code=status.HTTP_200_OK)
async def app_req_upload(requirements: AppRequirements, biscuit: Annotated[str | None, Header()] = None) -> int:
    authorize(biscuit)

    app_req_id = 69
    return app_req_id


@app.put("/v1/app_requirements", status_code=status.HTTP_200_OK)
async def app_req_update(requirements: AppRequirements, biscuit: Annotated[str | None, Header()] = None):
    authorize(biscuit)

    app_req_id = 69
    return app_req_id


@app.get("/v1/app_reqs_id", status_code=status.HTTP_200_OK)
async def app_req_get(biscuit: Annotated[str | None, Header()] = None) -> AppRequirements:
    authorize(biscuit)

    app_req_id = 69
    return app_req_id


@app.get("/v1/ec_fe", status_code=status.HTTP_200_OK)
async def edge_cluster_ip_get(biscuit: Annotated[str | None, Header()] = None) -> str:
    authorize(biscuit)

    ecf_ip = '127.0.0.1'
    return ecf_ip

if __name__ == "__main__":
    uvicorn.run("main:app", host=conf.HOST, port=conf.PORT,
                reload=True, log_level=conf.LOG_LEVEL)


def authorize(biscuit):
    if biscuit == None:
        message = 'Missing biscuit token in header'
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=message)

    authorization = auth.authorize_biscuit(biscuit)

    if authorization != None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=authorization)
