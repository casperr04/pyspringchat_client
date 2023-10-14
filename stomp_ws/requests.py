import requests


class Requests:
    def __init__(self, config):
        self.config = config
        self.backendurl = config.get('backendurl')
        self.bearer = config.get('token')
        self.auth = {"Authorization": f"Bearer {self.bearer}"}

    def check_server_status(self):
        endpoint = f"{self.backendurl}/demo/controller/public"
        try:
            r = requests.get(endpoint)
        except requests.exceptions.ConnectionError:
            return False
        if r.status_code != 200:
            return False
        else:
            return True

    def check_if_in_server(self, channel_id):
        endpoint = f"{self.backendurl}/v1/channels/check/private-channel/{channel_id}"
        r = requests.get(endpoint, headers=self.auth)
        if r.status_code != 200:
            return False
        else:
            return True
