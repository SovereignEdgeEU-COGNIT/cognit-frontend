# cognit-frontend

Deploy using python virtual env

Install virtualenv

```bash
pip install virtualenv
```

Configure options at `/etc/cognit-frontend.conf`

```yaml
host: 0.0.0.0
port: 1338
one_xmlrpc: https://cognit-lab.sovereignedge.eu/RPC2
log_level: debug
```

Create virtualenv

```bash
cd /path/to/cognit-frontend
python -m venv venv
```

Load the virtual env (Bash)

```bash
source venv/bin/activate
```

Run the application

```bash
./src/main.py
```

Unload the virtual env

```bash
deactivate
```

