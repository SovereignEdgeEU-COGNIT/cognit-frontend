import pyone

ONE_XMLRPC = None  # Set when importing module
DOCUMENT_TYPES = {
    'APP_REQUIREMENT' : 1338
}

def create_client(user: str, password: str) -> pyone.OneServer:
    return pyone.OneServer(ONE_XMLRPC, session=f"{user}:{password}")

def authenticate(user: str, password: str) -> bool:
    one = create_client(user, password)

    try:
        one.userpool.info()
    except pyone.OneAuthenticationException as e:
        print(e)
        return False

    return True


def app_requirement_create(one: pyone.OneServer, app_requirement: dict) -> int :
    document_id = one.document.allocate(app_requirement, DOCUMENT_TYPES['APP_REQUIREMENT'])
    return document_id


def app_requirement_get(one: pyone.OneServer, document_id: int):
    document = one.document.info(document_id).TEMPLATE

    if int(document.TYPE) != DOCUMENT_TYPES['APP_REQUIREMENT']:
        raise

    return dict(document)


def app_requirement_update(one: pyone.OneServer, document_id: int, app_requirement: dict) -> int:
    app_requirement_get(one, document_id)

    document_id = one.document.update(app_requirement, 0)
    return document_id




def cluster_get(one: pyone.OneServer, cluster_id: int):
    cluster = one.cluster.info(cluster_id)

    return {
        'ID': cluster_id,
        'NAME': cluster.NAME,
        'HOSTS': cluster.HOST.ID,
        'DATASTORES': cluster.DATASTORES.ID,
        'VNETS' : cluster.VNETS.ID
    }

