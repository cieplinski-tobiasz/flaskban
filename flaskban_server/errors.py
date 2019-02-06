"""
The module defines hierarchy of errors used by application.
It also contains utility methods for handling errors and creating error responses.

Attributes:
    JWT_ERROR_HANDLER: Decorator for handling common authentication token errors.
    BAD_REQUEST_ERROR_HANDLER: Decorator for handling common malformed request errors.
"""

from http import HTTPStatus

from functools import wraps

from flask_jwt_extended.exceptions import JWTExtendedException
from jwt import PyJWTError
from marshmallow import ValidationError
from werkzeug.exceptions import BadRequest


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


def handle_error(*errors, status=HTTPStatus.INTERNAL_SERVER_ERROR, message=None):
    """
    Handles given errors by returning an error response consisting of given status and message.

    If during the execution of wrapped function an error will be raised,
    and the error is present in the *errors list,
    the error will be caught and error message will be returned
    instead of raising the error.

    Args:
        *errors (type): list of Exception classes to be handled.
        status (int): HTTP status used in the error message.
        message (str): Message used in the error message.

    Returns:
        function: wraps function in a given way:
                    - if exception from *errors is raised tuple from make_error_response function
                    - if no exception is raised, fun return value will be returned
    """
    def wrapper(fun):
        @wraps(fun)
        def handler(*args, **kwargs):
            try:
                return fun(*args, **kwargs)
            except errors as caught:
                if not message and hasattr(caught, 'message'):
                    return make_error_response(status, caught.message)

                return make_error_response(status, message)

        return handler

    return wrapper


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


class NotFoundError(ClientError):
    """
    Error raised when client tries to access a non-existing resource.
    """


class InconsistentDataError(ClientError):
    """
    Error raised when client sends inconsistent data in body,
    e.g. body refers to data that does not exist.
    """


JWT_ERROR_HANDLER = handle_error(JWTExtendedException, PyJWTError,
                                 status=HTTPStatus.UNAUTHORIZED,
                                 message='No valid token present')

BAD_REQUEST_ERROR_HANDLER = handle_error(BadRequest, ValidationError, InvalidDataError,
                                         status=HTTPStatus.BAD_REQUEST,
                                         message='Invalid request body')
