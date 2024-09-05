#!/usr/bin/env python3.11

import requests
from requests.auth import HTTPBasicAuth
import json

# get token

uri = 'http://localhost:1338/v1/authenticate'
user = 'oneadmin'
password = 'opennebula'

response = requests.post(uri, auth=HTTPBasicAuth(user, password))
token = response.json()

# upload app requirement

uri = 'http://localhost:1338/v1/app_requirements'
body = {
    'REQUIREMENT': 'cpu = amd',
    'SCHEDULING_POLICY': 'fast'
}
headers = {
    "token": token
}

response = requests.post(uri, data=json.dumps(body), headers=headers)
id = response.json()

# get app requirement

uri = f'http://localhost:1338/v1/app_requirements/{id}'

response = requests.get(uri, headers=headers)
print(response.json())

# update app requirement
body = {
    'REQUIREMENT': 'cpu = intel',
    'SCHEDULING_POLICY': 'slow'
}

response = requests.put(uri, data=json.dumps(body), headers=headers)

# get app requirement
response = requests.get(uri, headers=headers)
print(response.json())

# delete app requirement
response = requests.delete(uri, headers=headers)

# upload function
uri = 'http://localhost:1338/v1/daas/upload'
body = {
    "lang": "PY",
    "fc": "ZGVmIHNheV9oZWxsbygpOgogICAgcHJpbnQoJ2hlbGxvJykK",
    "fc_hash": "bacaa2c80e4f7f381117ff8503bd8752"
}

response = requests.post(uri, headers=headers, data=json.dumps(body))
