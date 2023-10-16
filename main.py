import sys
import time
from requests import RequestException
from websocket import WebSocketConnectionClosedException

import stomp_ws.commands
import stomp_ws.util as util
import stomp_ws.auth as auth
import logging
import stomp_ws.config as config
from stomp_ws import commands, requests, event
from stomp_ws.client import Client
from stomp_ws.frame import Frame
from requests import exceptions as ex

connected = False
get_events = True
destination_url_prefix = "/app/chat/"
events = []


def program_exit(msg=None, sleep=2):
    """
    Exits the program.
    """
    print(msg)
    time.sleep(sleep)
    sys.exit()


def chat_print(frame: Frame):
    """
    Callback function to print received chat messages.
    :param frame: Websocket Frame
    """
    body = frame.body
    global connected
    if not connected and body.author == 'SERVER' and body.msg == 'pong!':
        print("Successfully connected!")
        connected = True
        return
    print(f"----------------------\n"
          f"MSG:ID:{body.msg_id}\n"
          f"AUTHOR:{body.author}\n"
          f"MSG:{body.msg}\n")


def event_print(frame: Frame):
    """
    Callback function to print received events.
    :param frame: Websocket Frame
    """
    body = frame.body
    global connected
    if not connected and body.author == 'SERVER' and body.msg == 'pong!':
        print("Successfully connected!")
        connected = True
        return
    if get_events:
        logging.debug(f"----------------------\n"
                      f"EVENT_TYPE:{body.msg_id}\n"
                      f"DATE:{body.date}\n"
                      f"MSG:{body.msg}\n")
    else:
        event.Event(body.msg_id, body.date, body.msg)
        events.append(event)


def print_title():
    """
    Prints ASCII art of the programs title PySpringChat
    """
    print("  _____        _____            _              _____ _           _   \n"
          " |  __ \      / ____|          (_)            / ____| |         | |  \n"
          " | |__) |   _| (___  _ __  _ __ _ _ __   __ _| |    | |__   __ _| |_ \n"
          " |  ___/ | | |\___ \| '_ \| '__| | '_ \ / _` | |    | '_ \ / _` | __|\n"
          " | |   | |_| |____) | |_) | |  | | | | | (_| | |____| | | | (_| | |_ \n"
          " |_|    \__, |_____/| .__/|_|  |_|_| |_|\__, |\_____|_| |_|\__,_|\__|\n"
          "         __/ |      | |                  __/ |                       \n"
          "        |___/       |_|                 |___/                        \n")


def register_or_login_menu():
    """
    Menu loop that handles logging in and registering an account.
    """
    while True:
        util.clear()
        print_title()
        print("-Welcome to PySpringChat-\n")
        print("Type /register to register a new account\n")
        print("Type /login to login to an existing account\n")
        print("Type /exit to exit. \n")
        command = input()
        while True:
            match command:
                case "/register":
                    username = input("Enter your username:\n")
                    password = input("Enter your password:\n")
                    try:
                        return register(username, password)
                    except RequestException as e:
                        print(str(e))
                    return
                case "/login":
                    username = input("Enter your username:\n")
                    password = input("Enter your password:\n\n")
                    try:
                        return login(username, password)
                    except RequestException as e:
                        print("\n" + str(e) + "\n\n")
                        time.sleep(2)
                        register_or_login_menu()
                    return
                case "/exit":
                    program_exit("Goodbye!")
                case _:
                    print("Invalid command, please try again.")
            util.clear()


def main_menu():
    """
    Prints the welcome message
    """
    print("Welcome! Type /help to see the list of commands!\n")


def login(username, password):
    """
    Attempts to log in a user.
    :param username:
    :param password:
    :return: auth.User object
    """
    user = auth.User(config=config)
    user.login(password, username)
    return user


def register(username, password):
    """
    Attempts to register an user
    :param username:
    :param password:
    :return: auth.User object
    :return: auth.User object
    """
    user = auth.User(config)
    user.register(username, password)
    return user


def channel_loop(channel_headers, channel_unsubscribe, channel_commands, main_menu_commands: stomp_ws.commands.MainCommands):
    """
    Handles the chat input and channel commands.
    :param channel_commands
    :param main_menu_commands
    """
    print("\nJoined channel!\n\n")
    while True:
        try:
            if channel_commands.disconnected:
                menu_loop(main_menu_commands)
            msg = input("")
            if not channel_commands.command_handler(msg):
                channel_commands.channel_send(msg)
        except WebSocketConnectionClosedException:
            program_exit("Connection closed!")
        except KeyboardInterrupt:
            channel_commands.disconnect()
            program_exit(sleep=0)


def menu_loop(main_menu_commands: stomp_ws.commands.MainCommands):
    """
    Loop handling the main menu command handling
    :param main_menu_commands: MenuCommands object
    :return:
    """
    util.clear()
    print_title()
    while True:
        main_menu()
        inp = input()
        match inp:
            case '':
                continue
            case '/exit':
                program_exit("Goodbye!", 0)
            case '/logout':
                main_menu_commands.command_handler(inp)
                register_or_login_menu()
        match inp.split()[0]:
            case '/join_channel':
                try:
                    channel_headers, channel_unsubscribe, channel_commands = main_menu_commands.command_handler(inp)
                    util.clear()
                    channel_loop(channel_headers, channel_unsubscribe, channel_commands, main_menu_commands)
                except ex.RequestException:
                    print("Invalid channel id, try again!")
                    continue
                except TypeError:
                    print("Invalid channel id, try again!")
                    continue
        response = main_menu_commands.command_handler(inp)
        if response is None:
            continue
        elif not response:
            print("Invalid command, try again, or type /help to get a list of commands. \n")


def get_auth():
    """
    Handles the authentication of the user, connects them to WebSocket endpoint and subscribes them to the event channel.
    TODO: encapsulate those two into their own methods
    """
    config_dict = config.load_config('config.ini')
    req = requests.Requests(config)

    # noinspection PyBroadException
    if not req.check_server_status():
        program_exit("Server is down, try again later or contact the server owner!", 5)
    try:
        username = auth.try_token(config_dict.get("token"))
        if not username:
            user = register_or_login_menu()
        else:
            user = auth.User(config=config)
            user.username = username
            user.token = config_dict.get("token")
    # Weird exception chaining, need to catch broad exception for this
    except Exception as e:
        program_exit(f"Unable to connect to server, aborting, {e}")

    config_object = config.Config(user.token, None, user.username, url='http://localhost:8080',
                                  keep_token=True, config_dict=config_dict)
    config.write_config(config_object)
    config_dict = config.load_config('config.ini')
    config.config_object = config_object
    req = requests.Requests(config)
    client = Client("ws://localhost:8080/chat-test", {"Authorization": f"Bearer {config_dict.get('token')}"})
    main_menu_commands = commands.MainCommands(client, user, req, config)
    client.connect(login="kacper",
                   passcode="45C82C421EBA87C8131E220F878E4145",
                   timeout=0)

    print(f"Logged in as {user.username}")

    event_headers, event_unsubscribe = client.subscribe(destination=f"/user/{user.username}/queue/event",
                                                        headers={"channel": "0"},
                                                        callback=event_print)

    client.send("/app/event", body="PING CHANNEL", headers={"channel": "0"})
    menu_loop(main_menu_commands)


if __name__ == '__main__':
    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
    config_dict = config.load_config('config.ini')
    get_auth()
