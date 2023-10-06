from datetime import time


class ChannelCommands:
    def channel_send(self, msg):
        self.client.send(self.destination_url, body=msg, headers={"channel": str(self.destination_id)})

    def disconnect(self):
        self.unsubscribe()
        print("Disconnected from channel")
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
        self.destination_id = destination_id
        self.disconnected = False
        self.commands = {"/ping": self.ping_command, "/exit": self.exit_command}


class MainCommands:
    def command_handler(self, command: str):
        commands = self.commands
        split_commands = str.split(command)
        if split_commands[0] not in commands:
            return False
        if len(split_commands) > 1:
            return_val = commands[split_commands[0]](split_commands[1])
        else:
            return_val = commands[command]()
        if return_val is None:
            return None
        else:
            return return_val

    def help(self):
        for k, v in self.commands_help.items():
            print(f"{k} - {v}")
        print("\n")

    def join_channel(self, destination_id):
        from main import chat_print, destination_url_prefix
        channel_headers, channel_unsubscribe = self.client.subscribe(
            destination=f"/user/{self.user.username}/queue/chat/{destination_id}",
            headers={"channel": str(destination_id)},
            callback=chat_print)
        channel_commands = ChannelCommands(self.client, channel_headers, channel_unsubscribe,
                                           f"{destination_url_prefix}{destination_id}",
                                           destination_id)
        return channel_headers, channel_unsubscribe, channel_commands

    def __init__(self, client, user):
        self.commands_help = {"/help": "Get list of commands",
                              "/join_channel [channel-id]": "Join a specified channel",
                              "/private-channels": "Get a list of your private channels",
                              "/user-info {user-id}": "Get info about a user",
                              "/log-out": "Logs you out.",
                              "/exit": "Exits PySpringChat"}

        self.commands = {"/help": self.help,
                         "/join_channel": self.join_channel}
                         # "/private_channels": self.private_channels,
                         # "/user_info": self.user_info,
                         # "/log_out": self.log_out}

        self.client = client
        self.user = user
