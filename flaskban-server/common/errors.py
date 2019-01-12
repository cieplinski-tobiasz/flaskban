"""
The module defines hierarchy of errors used by application.
It also contains utility methods for handling errors and creating error responses.
"""

from http import HTTPStatus

from functools import wraps


def make_error_response(status, message):
    """
    Makes a response tuple from HTTP status and message.

    Args:
        status (int): HTTP status of the response.
        message (str): Message describing the response.

    Returns:
        tuple: Two element tuple, the first element is a dictionary
               consisting of status and message,
               while the second element is a status.
    """
    return {'status': status, 'message': message}, status


class ClientError(Exception):
    """
    Base class for all exceptions raised because of client-side error.

    Attributes:
        message (str): Description of the error.
    """
    def __init__(self, message):
        """
        Inits ClientError with message.
        """
        super().__init__()
        self.message = message


class InvalidDataError(ClientError):
    """
    Error raised when client's request is malformed, e.g. required fields are missing.
    """


class AlreadyExistsError(ClientError):
    """
    Error raised when client tries to create a resource which already exists.
    """


class UnauthorizedError(ClientError):
    """
    Error raised when authentication token is not valid.
    """
