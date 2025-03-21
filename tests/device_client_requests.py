#!/usr/bin/env python3.11

import requests
from requests.auth import HTTPBasicAuth
import json
import os

conf_path = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'conf.json')
with open(conf_path, 'r') as file:
    CONF = json.load(file)


def authenticate(user: str, password: str):
    print(f"Requesting token for {user}")

    uri = f'{CONF["api_endpoint"]}/v1/authenticate'

    response = requests.post(uri, auth=HTTPBasicAuth(user, password))
    token = response.json()

    # inspect_response(response)

    return token


def app_req_upload(token: str, body: dict):
    print(f"Uploading application requirements {body}")

    uri = f'{CONF["api_endpoint"]}/v1/app_requirements'
    headers = {"token": token}

    response = requests.post(uri, headers=headers, data=json.dumps(body))
    id = response.json()

    inspect_response(response)

    return id


def app_req_read(token: str, id: int):
    print(f"Reading application requirements {id}")

    uri = f'{CONF["api_endpoint"]}/v1/app_requirements/{id}'
    headers = {"token": token}

    response = requests.get(uri, headers=headers)
    app_requirement = response.json()

    inspect_response(response)

    return app_requirement


def app_req_update(token: str, id: int, body: dict):
    print(f"Updating application requirements {body}")

    uri = f'{CONF["api_endpoint"]}/v1/app_requirements/{id}'
    headers = {"token": token}

    response = requests.put(uri, headers=headers, data=json.dumps(body))

    inspect_response(response)


def app_req_delete(token: str, id: int):
    print(f"Deleting application requirements {id}")

    uri = f'{CONF["api_endpoint"]}/v1/app_requirements/{id}'
    headers = {"token": token}

    response = requests.delete(uri, headers=headers)

    inspect_response(response)

    return response


def function_upload(token: str, body: dict):
    print(f"Uploading function {body}")

    uri = f'{CONF["api_endpoint"]}/v1/daas/upload'
    headers = {"token": token}

    response = requests.post(uri, headers=headers, data=json.dumps(body))
    id = response.json()

    inspect_response(response)

    return id

def cluster_get(token: str, app_req_id: int):
    print(f"Obtaining Cluster for {app_req_id}")

    uri = f'{CONF["api_endpoint"]}/v1/app_requirements/{app_req_id}/ec_fe'
    headers = {"token": token}

    response = requests.get(uri, headers=headers)
    id = response.json()

    inspect_response(response)

    return id


def inspect_response(response: requests.Response):
    print(f"Response Code: {response.status_code}")
    if response.status_code != 204:
        print(f"Response Body: {response.json()}")


credentials = CONF['credentials'].split(':')
token = authenticate(credentials[0], credentials[1])

app_req_id = app_req_upload(token, CONF['app_requirements'][0])
app_req_read(token, app_req_id)
app_req_update(token, app_req_id, CONF['app_requirements'][1])
app_req_read(token, app_req_id)
app_req_delete(token, app_req_id)
app_req_read(token, app_req_id)

function_upload(token, CONF['functions']['py'])

cluster_get(token, app_req_id)
