"""
The module contains resources that implement HTTP methods
allowing for manipulation of domain objects and retrieving entities of them.
"""

# pylint: disable=no-self-use
# The reason for disabling self-use is that Flask-RESTful extension
# expects HTTP methods declared as methods of the Resource subclass.
# Without the self argument, the routing does not work as expected.

from http import HTTPStatus

from flask import request
from flask_jwt_extended import jwt_required
from flask_restful import Resource
from marshmallow import EXCLUDE

import domain.models
import domain.schemas
import errors


class Board(Resource):
    """
    Defines methods for /boards/{board_id} endpoint.

    Every method for this endpoint requires the authentication token
    to be present in `Authorization` header.

    Properties:
        method_decorators: Decorators applied to every method in this class.
    """

    method_decorators = [
        jwt_required, errors.JWT_ERROR_HANDLER, errors.BAD_REQUEST_ERROR_HANDLER,
        errors.handle_error(errors.NotFoundError, status=HTTPStatus.NOT_FOUND),
    ]

    def get(self, board_id):
        """
        Retrieve the board.
        ---
        description: Returns board with given id, if user requesting it has permissions to see it.
                     Requires an authentication token in Authorization header.
        tags:
          - board
        security:
          - bearerAuth: []
        parameters:
          - in: path
            name: board_id
            schema:
              type: integer
            required: true
            description: ID of the board.
        responses:
          '200':
            description: Board object.
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/Board'
          '401':
            $ref: '#/components/responses/NoToken'
          '403':
            description: Returned when user has no permissions to see the board.
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/Error'
            examples:
              No permission:
                status: 403
                message: Forbidden - no permission to retrieve the board.
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
        """
        board = domain.models.Board.find_by_id(board_id)
        return domain.schemas.BOARD_SCHEMA.dump(board), HTTPStatus.OK

    def patch(self, board_id):
        """
        Change the name or visibility of the board.
        ---
        description: Changes the properties of board, if user has permissions to do it.
                     Only name and visibility can be changed - extra fields are ignored.
                     Requires an authentication token in Authorization header.
        tags:
          - board
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
          required: true
          description: The only fields taken in consideration
                       are name and visibility. Extra fields are ignored.
          content:
            application/json:
              schema:
                properties:
                  name:
                    type: string
                    example: School board
                  visibility:
                    type: string
                    enum: [public, private]
                    example: private
        responses:
          '200':
            description: Board modified successfully. Returns the modified board.
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/Board'
          '401':
            $ref: '#/components/responses/NoToken'
          '403':
            description: Returned when user has no permissions to modify the board.
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/Error'
            examples:
              No permission:
                status: 403
                message: Forbidden - no permission to modify the board
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
        """
        body = request.get_json()
        request_board = domain.schemas.BOARD_SCHEMA.load(body, partial=True, unknown=EXCLUDE)
        db_board = domain.models.Board.find_by_id(board_id)
        db_board.merge(request_board)
        return domain.schemas.BOARD_SCHEMA.dump(db_board), HTTPStatus.OK

    def delete(self, board_id):
        """
        Delete the board.
        ---
        description: Deletes the board, if user has permissions to do it.
                     All the tasks and columns in the board are also deleted.
                     Requires an authentication token in Authorization header.
        tags:
          - board
        security:
          - bearerAuth: []
        parameters:
          - in: path
            name: board_id
            schema:
              type: integer
            required: true
            description: ID of the board.
        responses:
          '204':
            description: Returned on successful deletion of the board. The response has no body.
          '401':
            $ref: '#/components/responses/NoToken'
          '403':
            description: Returned when user has no permissions to delete the board.
            content:
              application/json:
                schema:
                  $ref: '#/components/schema/Error'
            examples:
              No permission:
                status: 403
                message: Forbidden - no permission to delete the board
          '404':
            description: Returned when no board with given id exists.
            content:
              application/json:
                schema:
                  $ref: '#/definitions/Error'
            examples:
              No board:
                status: 404
                message: Board with id 1 does not exist
        """
        domain.models.Board.delete(board_id)
        return {}, HTTPStatus.NO_CONTENT


class Column(Resource):
    """
    Defines methods for /boards/{board_id}/columns/{column_id} endpoint.

    Every method for this endpoint requires the authentication token
    to be present in `Authorization` header.

    Properties:
        method_decorators: Decorators applied to every method in this class.
    """

    method_decorators = [
        jwt_required, errors.JWT_ERROR_HANDLER, errors.BAD_REQUEST_ERROR_HANDLER,
        errors.handle_error(errors.NotFoundError, status=HTTPStatus.NOT_FOUND),
    ]

    def get(self, board_id, column_id):
        """
        Retrieve the column.
        ---
        description: Returns column with given id, if user requesting it has permissions to do it.
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
          - in: path
            name: column_id
            schema:
              type: integer
            required: true
            description: ID of the column.
        responses:
          '200':
            description: Column successfully retrieved.
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/Column'
          '401':
            $ref: '#/components/responses/NoToken'
          '403':
            description: Returned when user has no permissions to retrieve the column.
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/Error'
            examples:
              No permission:
                status: 403
                message: Forbidden - no permission to retrieve the column.
          '404':
            description: Returned when no board or column with given id exists.
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/Error'
            examples:
              No board:
                status: 404
                message: Board with id 1 does not exist
              No column:
                status: 404
                message: Column with id 1 does not exist in board with id 1
        """
        column = domain.models.Column.find_by_ids(board_id=board_id, column_id=column_id)
        return domain.schemas.COLUMN_SCHEMA.dump(column), HTTPStatus.OK

    def delete(self, board_id, column_id):
        """
        Delete the column.
        ---
        description: Deletes the column, if user has permissions to do it.
                     All the tasks in the column are also deleted.
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
          - in: path
            name: column_id
            schema:
              type: integer
            required: true
            description: ID of the column.
        responses:
          '204':
            description: Column successfully deleted. The response has no body.
          '401':
            $ref: '#/components/responses/NoToken'
          '403':
            description: Returned when user has no permissions to delete the column.
            content:
              application/json:
                schema:
                  $ref: '#/components/schema/Error'
            examples:
              No permission:
                status: 403
                message: Forbidden - no permission to delete the column
          '404':
            description: Returned when no board or column with given id exists.
            content:
              application/json:
                schema:
                  $ref: '#/components/schema/Error'
            examples:
              No board:
                status: 404
                message: Board with id 1 does not exist
              No column:
                status: 404
                message: Column with id 1 does not exist in board with id 1
        """
        domain.models.Column.delete(board_id=board_id, column_id=column_id)
        return {}, HTTPStatus.NO_CONTENT

    def patch(self, board_id, column_id):
        """
        Change the name of the column.
        ---
        description: Changes the properties of the column, if user has permissions to do it.
                     Only name can be changed - extra fields are ignored.
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
          - in: path
            name: column_id
            schema:
              type: integer
            required: true
            description: ID of the column.
        requestBody:
          required: true
          description: The only field taken in consideration is name. Extra fields are ignored.
          content:
            application/json:
              schema:
                properties:
                  name:
                    type: string
                    example: Done
        responses:
          '200':
            description: Column modified successfully. Returns the modified column.
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/Column'
          '401':
            $ref: '#/components/responses/NoToken'
          '403':
            description: Returned when user has no permissions to modify the column.
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/Error'
            examples:
              No permission:
                status: 403
                message: Forbidden - no permission to modify the column
          '404':
            description: Returned when no board or column with given id exists.
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/Error'
            examples:
              No board:
                status: 404
                message: Board with id 1 does not exist
              No column:
                status: 404
                message: Column with id 1 does not exist in board with id 1
        """
        body = request.get_json()
        request_column = domain.schemas.COLUMN_SCHEMA.load(body, partial=True, unknown=EXCLUDE)
        db_column = domain.models.Column.find_by_ids(board_id=board_id, column_id=column_id)
        db_column.merge(request_column)
        return domain.schemas.COLUMN_SCHEMA.dump(db_column), HTTPStatus.OK


class Task(Resource):
    """
    Defines methods for /boards/{board_id}/tasks/{task_id} endpoint.

    Every method for this endpoint requires the authentication token
    to be present in `Authorization` header.

    Properties:
        method_decorators: Decorators applied to every method in this class.
    """

    method_decorators = [
        jwt_required, errors.JWT_ERROR_HANDLER, errors.BAD_REQUEST_ERROR_HANDLER,
        errors.handle_error(errors.NotFoundError, status=HTTPStatus.NOT_FOUND),
    ]

    def get(self, board_id, task_id):
        """
        Retrieve the task.
        ---
        description: Returns task with given id, if user requesting it has permissions to do it.
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
          - in: path
            name: task_id
            schema:
              type: integer
            required: true
            description: ID of the task.
        responses:
          '200':
            description: Task successfully retrieved.
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/Task'
          '401':
            $ref: '#/components/responses/NoToken'
          '403':
            description: Returned when user has no permissions to retrieve the task.
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/Error'
            examples:
              No permission:
                status: 403
                message: Forbidden - no permission to retrieve the task
          '404':
            description: Returned when no board or task with given id exists.
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/Error'
            examples:
              No board:
                status: 404
                message: Board with id 1 does not exist
              No task:
                status: 404
                message: Task with id 1 does not exist in board with id 1
        """
        task = domain.models.Task.find_by_ids(board_id=board_id, task_id=task_id)
        return domain.schemas.TASK_SCHEMA.dump(task), HTTPStatus.OK

    def delete(self, board_id, task_id):
        """
        Delete the task.
        ---
        description: Deletes the task, if user has permissions to do it.
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
          - in: path
            name: task_id
            schema:
              type: integer
            required: true
            description: ID of the task.
        responses:
          '204':
            description: Task successfully deleted. The response has no body.
          '401':
            $ref: '#/components/responses/NoToken'
          '403':
            description: Returned when user has no permissions to delete the task.
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/Error'
            examples:
              No permission:
                status: 403
                message: Access forbidden - no permission to delete the task
          '404':
            description: Returned when no board or task with given id exists.
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/Error'
            examples:
              No board:
                status: 404
                message: Board with id 1 does not exist
              No task:
                status: 404
                message: Task with id 1 does not exist
        """
        domain.models.Task.delete(board_id=board_id, task_id=task_id)
        return {}, HTTPStatus.NO_CONTENT

    @errors.handle_error(errors.AlreadyExistsError, errors.InconsistentDataError,
                         status=HTTPStatus.CONFLICT)
    def patch(self, board_id, task_id):
        """
        Change the properties of the task.
        ---
        description: Changes the properties of the task, if user has permissions to do it.
                     Every field except id can be changed.
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
          - in: path
            name: task_id
            schema:
              type: integer
            required: true
            description: ID of the task.
        requestBody:
          required: true
          description: The fields taken into consideration are
                       "column_id", "description", "name" and "user_id".
                       Extra fields are ignored. User id, column id and name
                       must be valid, i.e. user with given id
                       must be permitted to be assigned to the task,
                       column with given must exist within the board
                       and name of the task must be unique within the column.
          content:
            application/json:
              schema:
                properties:
                  name:
                    type: string
                    example: "Fix the bug"
                  description:
                    type: string
                    example: "Deadline at 6 p.m."
                  column_id:
                    type: integer
                    example: 4
                  user_id:
                    type: integer
                    example: 6
        responses:
          '200':
            description: Task modified successfully. Returns the modified task.
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/Task'
          '401':
            $ref: '#/components/responses/NoToken'
          '403':
            description: Returned when user has no permissions to modify the task.
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/Error'
            examples:
              No permission:
                status: 403
                message: Access forbidden - no permission to modify the task
          '404':
            description: Returned when no board or task with given id exists.
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/Error'
            examples:
              No board:
                status: 404
                message: Board with id 1 does not exist
              No task:
                status: 404
                message: Task with id 1 does not exist
          '409':
            description: Returned when no column with
                         given column_id exists, or user with given user_id
                         does not exist or is not permitted to be assigned to a task.
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/Error'
            examples:
              No column:
                status: 409
                message: Column with id 1 does not exist
              No user:
                status: 409
                message: User with id 1 does not exist
              Insufficient permissions for user:
                status: 409
                message: User with id 1 cannot be assigned to a task
              Task already exists:
                status: 409
                message: Task with name "Do the shopping" already exists in column with id 1
        """
        body = request.get_json()
        request_task = domain.schemas.TASK_SCHEMA.load(body, partial=True, unknown=EXCLUDE)
        db_task = domain.models.Task.find_by_ids(board_id=board_id, task_id=task_id)
        db_task.merge(request_task)
        return domain.schemas.TASK_SCHEMA.dump(db_task), HTTPStatus.OK
