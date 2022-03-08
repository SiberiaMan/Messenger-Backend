class NotPasswordLogin(Exception):
    def __init__(self, text: str):
        self.text = text


class WrongLoginPassword(Exception):
    pass


class LoginAlreadyTaken(Exception):
    pass
