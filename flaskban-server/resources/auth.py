from common.errors import InvalidDataError, AlreadyExistsError, UnauthorizedError, make_error_response
from flask import request
from flask_restful import Resource
from http import HTTPStatus
from marshmallow import ValidationError
from models.users import login_schema, register_schema, login, register
from werkzeug.exceptions import BadRequest


class Login(Resource):
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
            description: Either email or username must be filled. If both are present, username is used.
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
                  example: eyJh.eyJzdWIiOiIxMjM0NTY3ODkaW4iOnRydWV9.TJVA95OrM7E2cBab30RMHrHDcEfxjoYZg
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
        try:
            body = request.get_json()
            user = login_schema.load(body)
            token = login(user)
            return {'token': token}, HTTPStatus.OK
        except (BadRequest, ValidationError, InvalidDataError):
            return make_error_response(HTTPStatus.BAD_REQUEST, 'Invalid request body')
        except UnauthorizedError as e:
            return make_error_response(HTTPStatus.UNAUTHORIZED, e.message)


class Register(Resource):
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
            description: Both username and e-mail are required. Account will not be created if there exist a user
                         using the same username or email.
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
        try:
            body = request.get_json()
            user_pwd_hash, user_no_pwd_hash = register_schema.load(body), login_schema.load(body)
            register(user_pwd_hash)
            token = login(user_no_pwd_hash)
            return {'token': token}, HTTPStatus.CREATED
        except (BadRequest, ValidationError, InvalidDataError):
            return make_error_response(HTTPStatus.BAD_REQUEST, 'Invalid request body')
        except AlreadyExistsError as e:
            return make_error_response(HTTPStatus.CONFLICT, e.message)
