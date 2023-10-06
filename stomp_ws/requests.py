import requests
from stomp_ws import config


def check_server_status():
    endpoint = f"{config.config.get('backendurl')}/demo/controller/public"
    r = requests.get(endpoint)
    if r.status_code != 200:
        return False
    else:
        return True