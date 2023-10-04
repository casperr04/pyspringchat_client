import sys
import time
import schedule
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


if __name__ == '__main__':
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
    channel_commands = ChannelCommands(client, channel_headers, channel_unsubscribe, "/app/chat/1", 1)

    while True:
        try:
            if channel_commands.disconnected:
                exit()
            msg = input("")
            if not channel_commands.command_handler(msg):
                commands.channel_send(msg, client)
        except WebSocketConnectionClosedException:
            print("Connection closed!")
        except KeyboardInterrupt:
            channel_commands.disconnect()
            break
