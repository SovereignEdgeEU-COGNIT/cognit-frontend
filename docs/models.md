Credentials object:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "auth_creds": {
      "type": "object",
      "properties": {
        "usr": {"type":"string"},
        "passwd": {"type":"string"}
      }
    }
  }
}
```

App requirements object

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "app_reqs": {
      "type": "object",
      "properties": {
        "requirement": {"type":"string"},
        "scheduling_policy": {"type":"string"}
      }
    }
  }
}
```

Assigned ECF object

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "edge_cluster_frontend": {
      "type": "object",
      "properties": {
        "ecf_id": {"type":"integer"},
        "ip_address": {"type":"string"},
      }
    }
  }
}
```

Biscuit token object

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "biscuit_token": {
      "type": "object",
      "properties": {
        "authority_block": {"type":"string"},
        "revocation_id": {"type":"string"},
        "signed_by": {"type":"string"}
      }
    }
  }
}  
```
