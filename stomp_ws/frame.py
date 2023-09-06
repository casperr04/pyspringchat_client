from urllib.parse import urlparse

Byte = {
    'LF': '\x0A',
    'NULL': '\x00'
}

class Message:

    def __init__(self, author, msg_id, date, msg):
        self.author = author
        self.msg_id = msg_id
        self.date = date
        self.msg = msg

class Frame:

    def __init__(self, command, headers, body):
        self.command = command
        self.headers = headers
        self.body = '' if body is None else body

    def __str__(self):
        lines = [self.command]
        skipContentLength = 'content-length' in self.headers
        if skipContentLength:
            del self.headers['content-length']

        for name in self.headers:
            value = self.headers[name]
            lines.append("" + name + ":" + value)

        if self.body is not None and not skipContentLength:
            lines.append("content-length:" + str(len(self.body)))

        lines.append(Byte['LF'] + self.body)
        return Byte['LF'].join(lines)

    @staticmethod
    def unmarshall_single(data):
        lines = data.split(Byte['LF'])

        command = lines[0].strip()
        headers = {}

        # get all headers
        i = 1
        while lines[i] != '':
            # get key, value from raw header
            (key, value) = lines[i].split(':')
            headers[key] = value
            i += 1

        #Return body as a message class 
        # set body to None if there is no body
        if(lines[i+1] == Byte["NULL"]):
            body = None
        else:
            auth = lines[i + 1] 
            id = lines[i + 2]
            date = lines[i + 3]
            msg = lines[i + 4]
            body = Message(auth, id, date, msg)
            
        return Frame(command, headers, body)

    @staticmethod
    def marshall(command, headers, body):
        return str(Frame(command, headers, body)) + Byte['NULL']
