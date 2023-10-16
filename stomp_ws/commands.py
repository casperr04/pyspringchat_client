from requests import exceptions
import stomp_ws.exception as ex
import main
import stomp_ws.config as conf


class ChannelCommands:
    """
    Class for handling the commands while in a channel
    """
    def channel_send(self, msg):
        """
        Sends a message to the currently connected channel.
        :param msg:
        :return:
        """
        self.client.send(self.destination_url, body=msg, headers={"channel": str(self.destination_id)})

    def disconnect(self):
        """
        Disconnects from the connected channel
        :return:
        """
        self.unsubscribe()
        print("Disconnected from channel\n")
        self.disconnected = True

    def ping_command(self):
        """
        Pings the channel
        :return:
        """
        channel_send("/ping_channel", self.client)

    def exit_command(self):
        """
        Handles the command for disconnecting from the channel.
        :return:
        """
        self.disconnect()

    def command_handler(self, command) -> bool:
        """
        Handles and executes given channel commands.
        :param command:
        :return:
        """
        commands = self.commands
        if command in commands:
            commands[command]()
            return True
        return False

    def __init__(self, client, headers, unsubscribe, destination_url, destination_id, req):
        self.client = client
        self.headers = headers
        self.unsubscribe = unsubscribe
        self.destination_url = destination_url
        self.destination_id = destination_id
        self.req = req
        self.disconnected = False
        self.commands = {"/ping": self.ping_command, "/exit": self.exit_command}


class MainCommands:
    """
    Class for handling main menu commands and executing them.
    """
    def command_handler(self, command: str):
        """
        Parses and executes a given command
        :param command:
        :return:
        """
        commands = self.commands
        split_commands = str.split(command)
        if split_commands[0] not in commands:
            return False
        if len(split_commands) > 1:
            return_val = commands[split_commands[0]](split_commands[1])
        else:
            try:
                return_val = commands[command]()
            except TypeError:
                return False
        if return_val is None:
            return None
        else:
            return return_val

    def help(self):
        """
        Prints all the main menu commands
        :return:
        """
        for k, v in self.commands_help.items():
            print(f"{k} - {v}")
        print("\n")

    def join_channel(self, destination_id):
        """
        Joins a specified channel
        :param destination_id: Channel ID
        :return:
        """
        from main import chat_print, destination_url_prefix
        if not self.req.check_if_in_server(destination_id):
            raise exceptions.RequestException

        channel_headers, channel_unsubscribe = self.client.subscribe(
            destination=f"/user/{self.user.username}/queue/chat/{destination_id}",
            headers={"channel": str(destination_id)},
            callback=chat_print)
        channel_commands = ChannelCommands(self.client, channel_headers, channel_unsubscribe,
                                           f"{destination_url_prefix}{destination_id}",
                                           destination_id, self.req)
        return channel_headers, channel_unsubscribe, channel_commands

    def logout(self):
        """
        Logs out the user
        :return:
        """
        conf.config_object.token = ""
        conf.config_object.username = ""
        conf.write_config(conf.config_object)
        print("Logged out\n")
        main.get_auth()

    def create_channel(self, username):
        """
        Creates a channel
        :param username:
        :return:
        """
        try:
            self.req.create_private_channel(username)
            print("\nChannel created\n")
        except ex.RequestException as e:
            print(e)

    def friend_request(self, username):
        """
        Sends a friend request
        :param username: Username of the user to send the request to
        :return:
        """
        try:
            self.req.friend_user(username)
            print("\nFriend request sent\n")
        except ex.RequestException as e:
            print(e)

    def __init__(self, client, user, req, config):
        self.commands_help = {"/help": "Get list of commands",
                              "/private-channels": "Get a list of your private channels",
                              "/friend_request [username]": "Sends a friend request to user",
                              "/create_channel [username]": "Create a private channel with a friend by his username",
                              "/join_channel [channel-id]": "Join a specified channel",
                              "/user-info [user-id]": "Get info about a user",
                              "/logout": "Logs you out",
                              "/exit": "Exits PySpringChat"}
        # "/private_channels": self.private_channels,
        # "/user_info": self.user_info,
        # "/log_out": self.log_out}
        self.client = client
        self.user = user
        self.req = req
        self.config = config
        self.commands = {"/help": self.help,
                         "/join_channel": self.join_channel,
                         "/logout": self.logout,
                         "/create_channel": self.create_channel,
                         "/friend_request": self.friend_request}
