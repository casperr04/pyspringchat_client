import json
import time

from stomp_ws.client import Client
import logging


def print_frame(frame):
    print(frame.body)


if __name__ == '__main__':
    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)

    # open transport
    client = Client("ws://localhost:8080/chat-test", {"Authorization": "Bearer 384a5af1-4cef-4ff3-bedf-557c9fffa407"})

    # connect to the endpoint
    client.connect(login="kacper",
                   passcode="45C82C421EBA87C8131E220F878E4145",
                   timeout=0)

    # subscribe channel
    client.subscribe("/user/kacper2/queue/chat/1", callback=print_frame, headers={"channel": "1"})
    client.send("/app/chat/1", body="yest", headers={"channel": "1"})
    while True:
        client.send("/app/chat/1", body=input("wait"), headers={"channel": "1"})
    # send msg to channel
    #client.send("/topic/kacper/chat/1", body=json.dumps({'name': 'tom'}))
    #client.send("/topic/chat/1", body="yeah")
