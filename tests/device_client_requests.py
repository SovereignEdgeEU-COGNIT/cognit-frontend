#!/usr/bin/env python3.11

import requests
import json

# get token

uri = 'http://localhost:1338/v1/authenticate'
body = {
    'user': 'oneadmin',
    'password': 'opennebula'
}

response = requests.post(uri, data=json.dumps(body))
token = response.json()

# upload app requirement

uri = 'http://localhost:1338/v1/app_requirements'
body = {
    'requirement': 'cpu = amd',
    'scheduling_policy': 'fast'
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
    'requirement': 'cpu = intel',
    'scheduling_policy': 'slow'
}

response = requests.put(uri, data=json.dumps(body), headers=headers)

# get app requirement
response = requests.get(uri, headers=headers)
print(response.json())

