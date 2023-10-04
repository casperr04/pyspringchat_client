import configparser

# Create a global configuration dictionary
config = {}
parser = configparser.ConfigParser(allow_no_value=True)


class Config:
    def __init__(self, token=None, refresh=None, username=None, url=None, keep_token=None, config_dict=None):
        self.token = token
        self.refresh = refresh
        self.username = username
        self.url = url
        self.config_dict = config_dict
        self.keep_token = keep_token if isinstance(keep_token, bool) else False


# Function to read and load the configuration file
def load_config(config_file_path: str) -> dict:
    global config
    parser.read(config_file_path)
    config = dict(parser.items('DEFAULT'))
    return config


def write_config(config_object: Config):
    parser['DEFAULT'] = {'token': config_object.token,
                         'refresh': config_object.refresh,
                         'username': config_object.username,
                         'backendUrl': config_object.url,
                         'keep-token': config_object.keep_token}
    with open('./config.ini', 'w') as configfile:
        parser.write(configfile)
