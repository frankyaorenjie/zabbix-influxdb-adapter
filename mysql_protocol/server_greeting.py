from mysql_protocol.base_payload import BasePayload


class ServerGreeting(BasePayload):
    def __init__(self):
        super().__init__()
