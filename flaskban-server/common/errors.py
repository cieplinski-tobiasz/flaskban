def make_error_response(status, message):
    return {'status': status, 'message': message}, status


class ClientError(Exception):
    def __init__(self, message):
        super().__init__()
        self.message = message


class InvalidDataError(ClientError):
    pass


class AlreadyExistsError(ClientError):
    pass


class UnauthorizedError(ClientError):
    pass
