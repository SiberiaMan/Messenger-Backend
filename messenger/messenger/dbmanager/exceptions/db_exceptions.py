

class ServiceUnavailable(Exception):
    def __init__(self):
        self.text = "SERVICE UNAVAILABLE"


class NotFoundChatsUsers(Exception):
    def __init__(self, msg: str):
        self.text = msg


class RepeatUserInChat(Exception):
    pass


class RepeatChat(Exception):
    pass
