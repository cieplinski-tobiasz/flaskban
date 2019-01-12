from http import HTTPStatus

from flask import request
from flask_restful import Resource
from marshmallow import ValidationError
from werkzeug.exceptions import BadRequest

from models.users import LOGIN_SCHEMA, REGISTER_SCHEMA, login, register
from errors import InvalidDataError, AlreadyExistsError, \
    UnauthorizedError, handle_error


class Login(Resource):
    method_decorators = [
        handle_error(BadRequest, ValidationError, InvalidDataError,
                     status=HTTPStatus.BAD_REQUEST, message='Invalid request body')
    ]

    @handle_error(UnauthorizedError, status=HTTPStatus.UNAUTHORIZED)
    def post(self):
        """
        Authenticate user.
        ---
        description: Supplies registered user with the authentication token.
        tags:
          - auth
        parameters:
          - in: body
            name: body
            description: Either email or username must be filled. If both are present,
                         username is used.
            schema:
              id: Credentials
              properties:
                username:
                  type: string
                  example: john_smith
                email:
                  type: string
                  format: email
                  example: john_smith@gmail.com
                password:
                  type: string
                  format: password
                  example: qwerty
                  required: true
        responses:
          200:
            description: Successful authentication resulting in the authentication token.
            schema:
              id: Token
              properties:
                token:
                  type: string
                  required: true
                  example: eyJh.eyJzdWIiOiIxMjM0NTY3ODkaW4iOnRydWV9.TJVA95OrM7E2cBab30RMHrHDcEfxjoYZ
          400:
            description: Returned when request body is invalid, e.g. has no required fields,
                         redundant extra fields or is malformed.
            schema:
              $ref: '#/definitions/Error'
            examples:
              Already exists: {
                status: 400,
                message: "Invalid request body"
              }
          401:
            description: Failed authentication.
            schema:
              id: Error
              properties:
                status:
                  type: integer
                  required: true
                message:
                  type: string
                  required: true
            examples:
              failure: {status: 401, message: "Wrong username or password"}
        """
        body = request.get_json()
        user = LOGIN_SCHEMA.load(body)
        token = login(user)
        return {'token': token}, HTTPStatus.OK


class Register(Resource):
    method_decorators = [
        handle_error(BadRequest, ValidationError, InvalidDataError,
                     status=HTTPStatus.BAD_REQUEST, message='Invalid request body')
    ]

    @handle_error(AlreadyExistsError, status=HTTPStatus.CONFLICT)
    def post(self):
        """
        Create new account.
        ---
        description: Creates an account and returns the authentication token.
        tags:
          - auth
        parameters:
          - in: body
            name: body
            description: Both username and e-mail are required. Account will not be created
                         if there exist a user using the same username or email.
            schema:
              $ref: '#/definitions/Credentials'
        responses:
          201:
            description: Account successfully created. Response contains the authentication token.
            schema:
              $ref: '#/definitions/Token'
          400:
            description: Returned when request body is invalid, e.g. has no required fields,
                         redundant extra fields or is malformed.
            schema:
              $ref: '#/definitions/Error'
            examples:
              Already exists: {
                status: 400,
                message: "Invalid request body"
              }
          409:
            description: Returned when user with given email or username already exists.
            schema:
              $ref: '#/definitions/Error'
            examples:
              Already exists: {
                status: 409,
                message: "User already exists"
              }
        """
        body = request.get_json()
        user_pwd_hash, user_no_pwd_hash = REGISTER_SCHEMA.load(body), LOGIN_SCHEMA.load(body)
        register(user_pwd_hash)
        token = login(user_no_pwd_hash)
        return {'token': token}, HTTPStatus.CREATED
