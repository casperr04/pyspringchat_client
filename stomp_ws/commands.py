from datetime import time


class ChannelCommands:
    def channel_send(self, msg):
        self.client.send(self.destination, body=msg, headers={"channel": str(self.destination_id)})

    def disconnect(self):
        self.unsubscribe()
        print("Goodbye!")
        self.disconnected = True

    def ping_command(self):
        channel_send("/ping_channel", self.client)

    def exit_command(self):
        self.disconnect()

    def command_handler(self, command) -> bool:
        commands = self.commands
        if command in commands:
            commands[command]()
            return True
        return False

    def __init__(self, client, headers, unsubscribe, destination_url, destination_id):
        self.client = client
        self.headers = headers
        self.unsubscribe = unsubscribe
        self.destination_url = destination_url
        self.destination_id = destination_url
        self.disconnected = False
        self.commands = {"/ping": self.ping_command, "/exit": self.exit_command}
