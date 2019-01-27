"""
The module contains resources that implement HTTP methods
allowing for authentication, i.e. login and registration.
"""

# pylint: disable=no-self-use
# The reason for disabling self-use is that Flask-RESTful extension
# expects HTTP methods declared as methods of the Resource subclass.
# Without the self argument, the routing does not work as expected.

from http import HTTPStatus

from flask import request
from flask_restful import Resource

from domain.models import User
import domain.schemas
import errors


class Login(Resource):
    """
    Defines methods for /auth/login endpoint.

    Properties:
        method_decorators: Decorators applied to every method in this class.
    """

    method_decorators = [errors.BAD_REQUEST_ERROR_HANDLER]

    @errors.handle_error(errors.UnauthorizedError, status=HTTPStatus.UNAUTHORIZED)
    def post(self):
        """
        Authenticate user.
        ---
        description: Supplies registered user with the authentication token.
        tags:
          - auth
        requestBody:
          required: true
          description: Either email or username must be filled. If both are present,
                       username is used.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Credentials'
        responses:
          '200':
            description: Successful authentication resulting in the authentication token.
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/Token'
          '400':
                  $ref: '#/components/responses/InvalidRequest'
          '401':
            description: Failed authentication.
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/Error'
            examples:
              Failed authentication:
                status: 401
                message: Wrong username or password
        """
        body = request.get_json()
        user = domain.schemas.LOGIN_SCHEMA.load(body)
        token = User.login(user)
        return {'token': token}, HTTPStatus.OK


class Register(Resource):
    """
    Defines methods for /auth/register endpoint.

    Properties:
        method_decorators: Decorators applied to every method in this class.
    """

    method_decorators = [errors.BAD_REQUEST_ERROR_HANDLER]

    @errors.handle_error(errors.AlreadyExistsError, status=HTTPStatus.CONFLICT)
    def post(self):
        """
        Create new account.
        ---
        description: Creates an account and returns the authentication token.
        tags:
          - auth
        requestBody:
          required: true
          description: Both username and e-mail are required. Account will not be created
                       if there exist a user using the same username or email.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Credentials'
        responses:
          '201':
            description: Account successfully created. Response contains the authentication token.
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/Token'
          '400':
                  $ref: '#/components/responses/InvalidRequest'
          '409':
            description: Returned when user with given email or username already exists.
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/Error'
            examples:
              Already exists:
                status: 409
                message: User already exists
        """
        body = request.get_json()
        user_pwd_hash = domain.schemas.REGISTER_SCHEMA.load(body)
        user_no_pwd_hash = domain.schemas.LOGIN_SCHEMA.load(body)
        User.register(user_pwd_hash)
        token = User.login(user_no_pwd_hash)
        return {'token': token}, HTTPStatus.CREATED
