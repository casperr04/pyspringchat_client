import logging
import sys
import time
import schedule
import urllib3.exceptions
from websocket import WebSocketConnectionClosedException

import stomp_ws.auth as auth
import logging
import stomp_ws.config as config
from stomp_ws.client import Client
from stomp_ws.frame import Frame

connected = False
get_events = False

def chat_print(frame: Frame):
    body = frame.body
    global connected
    if not connected:
        if body.author == 'SERVER' and body.msg == 'pong!':
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
    if not connected:
        if body.author == 'SERVER' and body.msg == 'pong!':
            print("Successfully connected!")
            connected = True
            return
    if get_events:
        logging.debug(f"----------------------\n"
                      f"EVENT_TYPE:{body.msg_id}\n"
                      f"DATE:{body.date}\n"
                      f"MSG:{body.msg}\n")


def channel_send(message, this_client):
    this_client.send("/app/chat/1", body=message, headers={"channel": "1"})


def disconnect(this_client):
    channel_unsubscribe()
    this_client.disconnect()
    print("Goodbye!")
    time.sleep(2)
    if not connected:
        print("Cannot connect!")


def ping_command(this_client):
    channel_send("/ping_channel", this_client)


def exit_command():
    disconnect(client)

commands = {"/ping": ping_command, "/exit": exit_command}


def command_handler(command: str) -> bool:
    if command in commands:
        commands[command](client)
        return True
    return False

if __name__ == '__main__':
    config_dict = config.load_config('config.ini')
    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
    config_dict = config.load_config('config.ini')
    user = auth.User("kacper2")

    # noinspection PyBroadException
    # Weird exception chaining shenanigans, can't catch the exception without just using the base class.
    try:
        user.login("1234")
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

    while True:
        try:
            msg = input("")
            channel_send(msg, client)
        except WebSocketConnectionClosedException:
            print("Connection closed!")
        except KeyboardInterrupt:
            disconnect(client)
            break
