#!/usr/bin/env python

from fastapi import FastAPI, status, HTTPException, Header, Path, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import Annotated, Any
import uvicorn
import re
import requests
import json

import cognit_conf as conf
import biscuit_token as auth
import opennebula as one
from cognit_models import AppRequirements, EdgeClusterFrontend, ExecSyncParams

one.ONE_XMLRPC = conf.ONE_XMLRPC

# TODO: Update design doc

app = FastAPI(title='Cognit Frontend', version='0.1.0')
security = HTTPBasic()


@app.post("/v1/authenticate", status_code=status.HTTP_201_CREATED)
async def authenticate(credentials: Annotated[HTTPBasicCredentials, Depends(security)]) -> str:
    one.authenticate(credentials.username, credentials.password)

    token = auth.generate_token(credentials.username, credentials.password)
    return token


@app.post("/v1/app_requirements", status_code=status.HTTP_200_OK)
async def app_req_upload(
    requirements: AppRequirements,
    token: Annotated[str | None, Header()] = None
) -> int:

    client = authorize(token)

    return one.app_requirement_create(client, requirements.model_dump())


@app.put("/v1/app_requirements/{id}", status_code=status.HTTP_200_OK)
async def app_req_update(
    id: Annotated[int, Path(title="Document ID of the App Requirement")],
    requirements: AppRequirements,
    token: Annotated[str | None, Header()] = None
):

    client = authorize(token)

    one.app_requirement_update(client, id, requirements.model_dump())


@app.get("/v1/app_requirements/{id}", status_code=status.HTTP_200_OK, response_model=AppRequirements)
async def app_req_get(
    id: Annotated[int, Path(title="Document ID of the App Requirement")],
    token: Annotated[str | None, Header()] = None
) -> Any:

    client = authorize(token)

    return one.app_requirement_get(client, id)


@app.delete("/v1/app_requirements/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def app_req_get(
    id: Annotated[int, Path(title="Document ID of the App Requirement")],
    token: Annotated[str | None, Header()] = None
):

    client = authorize(token)

    return one.app_requirement_delete(client, id)


@app.get("/v1/app_requirements/{id}/ec_fe", status_code=status.HTTP_200_OK, response_model=EdgeClusterFrontend)
async def edge_cluster_get(
    id: Annotated[int, Path(title="Document ID of the App Requirement")],
    token: Annotated[str | None, Header()] = None
) -> Any:

    client = authorize(token)

    uri = conf.AI_ORCHESTRATOR_ENDPOINT
    body = {
        'app_requirement_id': id
    }
    # TODO: need clarification on how communication flow with AI orchestrator
    response = requests.get(uri, data=json.dumps(body), headers={
                            'Content-Type': 'application/json'})
    body = response.json()
    cluster_id = body['ID']

    cluster = one.cluster_get(client, cluster_id)

    return cluster


@app.post("/v1/daas/upload", status_code=status.HTTP_200_OK, response_model=EdgeClusterFrontend)
async def function_upload(
    function: ExecSyncParams,
    token: Annotated[str | None, Header()] = None
) -> int:

    client = authorize(token)

    return one.function_create(client, function.model_dump())

if __name__ == "__main__":
    uvicorn.run("main:app", host=conf.HOST, port=conf.PORT,
                reload=False, log_level=conf.LOG_LEVEL)


def authorize(token) -> list:
    if token == None:
        message = 'Missing token in header'
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=message)

    try:
        facts = auth.authorize_token(token)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    credentials = []
    matchers = [r'user\("([^"]*)"\)', r'password\("([^"]*)"\)']

    for regexp in matchers:
        match = re.search(regexp, facts)
        value = match.group(1) if match else None

        credentials.append(value)

    return one.create_client(credentials[0], credentials[1])
