from http import HTTPStatus

from flask import request
from flask_jwt_extended import jwt_required
from flask_restful import Resource

import domain.schemas
import errors


class Boards(Resource):
    """
    Defines methods for /boards endpoint.

    Every method for this endpoint requires the authentication token
    to be present in `Authorization` header.

    Properties:
        method_decorators: Decorators applied to every method in this class.
    """

    method_decorators = [
        handle_error(JWTExtendedException,
                     status=HTTPStatus.UNAUTHORIZED, message='No valid token present'),
        handle_error(BadRequest, ValidationError, InvalidDataError,
                     status=HTTPStatus.BAD_REQUEST, message='Invalid request body'),
        jwt_required
    ]

    def get(self):
        """
        List boards.
        ---
        description: Returns a list of boards, that user has access to,
                     i.e. public boards and private boards that allowed access to given user.
                     Requires an authentication token in Authorization header.
        tags:
          - board
        security:
          - bearerAuth: []
        parameters:
          - in: path
            name: offset
            schema:
              type: integer
            description: Index of first returned board from all search results. Defaults to 0.
          - in: path
            name: limit
            schema:
              type: integer
            description: Maximum number of results returned (acceptable values are 1 to 1000). Defaults to 20.
        responses:
          '200':
            description: List of boards. The board are presented in simplified name -
                         only "id", "name" and "visibility" are present in the result.
                         Endpoint for single board should be used in order to retrieve columns.
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/BoardList'
          '401':
            $ref: '#/components/responses/NoToken'
        """

    def post(self):
        """
        Create new board.
        ---
        description: Creates a new, empty kanban board and makes the user
                     who created it an administrator of the board.
                     Private boards cannot be seen by people without access,
                     while public boards may be seen by anybody.
                     Requires an authentication token in Authorization header.
        tags:
          - board
        security:
          - bearerAuth: []
        requestBody:
          content:
            application/json:
              schema:
                properties:
                  name:
                    type: string
                    required: true
                    example: My Wednesday Plan
                  visibility:
                    type: string
                    required: true
                    enum: [public, private]
          required: true
        responses:
          '201':
            description: Board created successfully. Returns the location
                         of newly created board in header,
                         and the object in response body.
            headers:
              Location:
                schema:
                  type: string
                  format: uri
                example: /boards/1
                description: Location of newly created board.
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/Board'
          '400':
            $ref: '#/components/responses/InvalidRequest'
          '401':
            $ref: '#/components/responses/NoToken'
        """
        body = request.get_json()
        board = domain.schemas.BOARD_SCHEMA.load(body)
        board.save()

        return domain.schemas.BOARD_SCHEMA.dump(board), HTTPStatus.CREATED,\
               {'Location': f'/boards/{board.id_}'}


class Columns(Resource):
    method_decorators = [jwt_required, errors.JWT_ERROR_HANDLER, errors.BAD_REQUEST_ERROR_HANDLER]

    @errors.handle_error(errors.NotFoundError, status=HTTPStatus.NOT_FOUND)
    @errors.handle_error(errors.AlreadyExistsError, status=HTTPStatus.CONFLICT)
    def post(self, board_id):
        """
        Create new column.
        ---
        description: Creates a new column in the board, if user has the permissions to do it.
                     Requires an authentication token in Authorization header.
        tags:
          - column
        security:
          - bearerAuth: []
        parameters:
          - in: path
            name: board_id
            schema:
              type: integer
            required: true
            description: ID of the board.
        requestBody:
          content:
            application/json:
              schema:
                properties:
                  name:
                    type: string
                    required: true
                    example: To do
          description: The name of the column is required,
                       and it has to be unique within the board.
          required: true
        responses:
          '201':
            description: Column successfully created. Returns the location
                         of newly created column in header,
                         and the object in response body.
            headers:
              Location:
                schema:
                  type: string
                  format: uri
                example: /boards/1/columns/1
                description: Location of newly created column.
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/Column'
          '400':
            $ref: '#/components/responses/InvalidRequest'
          '401':
            $ref: '#/components/responses/NoToken'
          '403':
            description: Returned when user has no permissions to create the column.
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/Error'
            examples:
              No permission:
                status: 403
                message: Forbidden - no permission to create the column
          '404':
            description: Returned when no board with given id exists.
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/Error'
            examples:
              No board:
                status: 404
                message: Board with id 1 does not exist
          '409':
            description: Returned when column with given name already exists.
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/Error'
            examples:
              Column already exists:
                status: 409
                message: Column with name "To do" already exists in board with id 1
        """
        body = request.get_json()
        column = domain.schemas.COLUMN_SCHEMA.load(body)
        column.save_to_board(board_id)

        return domain.schemas.COLUMN_SCHEMA.dump(column), HTTPStatus.CREATED, \
               {'Location': f'/boards/{board_id}/columns/{column.id_}'}


class Tasks(Resource):
    def post(self):
        """
        Create new task.
        ---
        description: Creates new task if the user has the permissions to do it.
                     Task is associated with board and column,
                     i.e. task can belong to *one* column only,
                     and to *one* board only.
                     Requires an authentication token in Authorization header.
        tags:
          - task
        security:
          - bearerAuth: []
        parameters:
          - in: path
            name: board_id
            schema:
              type: integer
            required: true
            description: ID of the board.
        requestBody:
          content:
            application/json:
              schema:
                properties:
                  name:
                    type: string
                    required: true
                    example: Take the rubbish out.
                  description:
                    type: string
                    example: Do it fast, it has been too long.
                  column_id:
                    type: integer
                    example: 1
                    required: true
                    description: ID of column that the task is assigned to.
                                 ID must be valid, i.e. a column with given id
                                 must exist within the board.
                  user_id:
                    type: integer
                    example: 4
                    description: ID of the user responsible for the task.
                                 The board must assign permissions for the user
                                 with given ID that allow him to be assigned to the task.
          required: true
          description: The name of the task is required.
                       User with given ID must be permitted by the board
                       to be able to be assigned to a given task.
                       Task's name must be unique within the column.
        responses:
          '201':
            description: Task successfully created. Returns the location of
                         newly created task in header,
                         and the object in response body.
            headers:
              Location:
                schema:
                  type: string
                  format: uri
                example: /boards/1/tasks/1
                description: Location of newly created task.
            schema:
              $ref: '#/components/schemas/Task'
          '401':
            $ref: '#/components/responses/NoToken'
          '403':
            description: Returned when user has no permissions to create the task.
            content:
              application/json:
                schema:
                  $ref: '#/definitions/Error'
            examples:
              No permission:
                status: 403
                message: Forbidden - no permission to create the task.
          '404':
            description: Returned when no board with given id exists.
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/Error'
            examples:
              No board:
                status: 404
                message: Not found - board with id 1 does not exist
          '409':
            description: Returned when task with given name
                         already exists within the column.
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/Error'
            examples:
              Task already exists:
                status: 409
                message: Task creation failed - task with a given name
                         already exists within column with id 1.
        """
