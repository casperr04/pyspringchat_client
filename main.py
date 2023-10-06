import sys
import time
from requests import RequestException
from websocket import WebSocketConnectionClosedException

import stomp_ws.auth as auth
import logging
import stomp_ws.config as config
from stomp_ws import commands
from stomp_ws.client import Client
from stomp_ws.commands import ChannelCommands
from stomp_ws.frame import Frame

connected = False
get_events = False


def chat_print(frame: Frame):
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
    print("  _____        _____            _              _____ _           _   \n"
          " |  __ \      / ____|          (_)            / ____| |         | |  \n"
          " | |__) |   _| (___  _ __  _ __ _ _ __   __ _| |    | |__   __ _| |_ \n"
          " |  ___/ | | |\___ \| '_ \| '__| | '_ \ / _` | |    | '_ \ / _` | __|\n"
          " | |   | |_| |____) | |_) | |  | | | | | (_| | |____| | | | (_| | |_ \n"
          " |_|    \__, |_____/| .__/|_|  |_|_| |_|\__, |\_____|_| |_|\__,_|\__|\n"
          "         __/ |      | |                  __/ |                       \n"
          "        |___/       |_|                 |___/                        \n")


def register_or_login_menu():
    while True:
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
                    password = input("Enter your password:\n")
                    try:
                        return login(username, password)
                    except RequestException as e:
                        print(str(e))
                    return
                case "/exit":
                    sys.exit()
                case _:
                    print("Invalid command, please try again.")


def main_menu():
    print("Welcome! Type /help to see the list of commands!\n")


def login(username, password):
    user = auth.User(username)
    user.login(password)
    return user


def register(username, password):
    user = auth.User(username)
    user.register(password)
    return user


def channel_loop(channel_headers, channel_unsubscribe, channel_commands):
    print("\nJoined channel!")
    while True:
        try:
            if channel_commands.disconnected:
                exit()
            msg = input("")
            if not channel_commands.command_handler(msg):
                channel_commands.channel_send(msg)
        except WebSocketConnectionClosedException:
            print("Connection closed!")
            sys.exit()
        except KeyboardInterrupt:
            channel_commands.disconnect()
            sys.exit()


def menu_loop():
    while True:
        util.clear()
        main_menu()
        inp = input()
        match inp.split()[0]:
            case '/join_channel':
                channel_headers, channel_unsubscribe, channel_commands = main_menu_commands.command_handler(inp)
                channel_loop(channel_headers, channel_unsubscribe, channel_commands)
                continue
            case '/exit':
                exit()
        response = main_menu_commands.command_handler(inp)
        if response is None:
            continue
        elif not response:
            print("Invalid command, try again, or type /help to get a list of commands. \n")


if __name__ == '__main__':
    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
    config_dict = config.load_config('config.ini')
    print_title()
    if not requests.check_server_status():
        print("Server is down, try again later or contact the server owner!")
        time.sleep(2)
        sys.exit()

    # noinspection PyBroadException
    try:
        if not user.try_token(config_dict.get("token")):
            user.login("1234")
            config_object = config.Config(user.token, None, user.username, url='http://localhost:8080', keep_token=True)
            config.write_config(config_object)
            config.config_dict = config_dict = config.load_config('config.ini')
        else:
            user.token = config_dict.get("token")
    # Weird exception chaining, need to catch broad exception for this
    except Exception:
        print("Unable to connect to server, aborting...")
        time.sleep(2)
        sys.exit()

    config_object = config.Config(user.token, None, user.username, url='http://localhost:8080', keep_token=True)
    config.write_config(config_object)
    client = Client("ws://localhost:8080/chat-test", {"Authorization": f"Bearer {config_dict.get('token')}"})
    client.connect(login="kacper",
                   passcode="45C82C421EBA87C8131E220F878E4145",
                   timeout=0)

    # subscribe channel (kacper2 is your username!!)
    # returns headers and unsubscribe()

    event_headers, event_unsubscribe = client.subscribe(destination=f"/user/{user.username}/queue/event",
                                                        headers={"channel": "0"},
                                                        callback=event_print)

    client.send("/app/event", body="PING CHANNEL", headers={"channel": "0"})

    channel_headers, channel_unsubscribe = client.subscribe(destination=f"/user/{user.username}/queue/chat/1",
                                                            headers={"channel": "1"},
                                                            callback=chat_print)
    channel_commands = ChannelCommands(client, channel_headers, channel_unsubscribe, "/app/chat/1", 1)

    while True:
        try:
            if channel_commands.disconnected:
                exit()
            msg = input("")
            if not channel_commands.command_handler(msg):
                commands.channel_send(msg)
        except WebSocketConnectionClosedException:
            print("Connection closed!")
        except KeyboardInterrupt:
            channel_commands.disconnect()
            break
