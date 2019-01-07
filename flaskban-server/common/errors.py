class ClientError(Exception):
    def __init__(self, message):
        self.message = message


class InvalidDataError(ClientError):
    pass


class AlreadyExistsError(ClientError):
    pass


class UnauthorizedError(ClientError):
    pass
