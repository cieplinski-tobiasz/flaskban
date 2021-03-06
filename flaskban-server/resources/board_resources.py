from flask_restful import Resource


class Board(Resource):
    def get(self, board_id):
        """
        Retrieve the board.
        ---
        description: Returns board with given id, if user requesting it has permissions to see it.
                     Requires a JWT Token in Authorization header.
        tags:
          - board
        security:
          -
        parameters:
          - in: path
            name: board_id
            type: integer
            required: true
            description: ID of the board.
        responses:
          200:
            description: Board object.
            schema:
              $ref: '#/definitions/Board'
          404:
            description: Returned when no board with given id exists.
            schema:
              $ref: '#/definitions/Error'
            examples:
              No board: {
                status: 404,
                message: 'Not found - board with id 1 does not exist.'
              }
          403:
            description: Returned when user has no permissions to see the board
                         or when JWT token is not present or is invalid.
            schema:
              $ref: '#/definitions/Error'
            examples:
              No permission: {
                status: 403,
                message: 'Access forbidden - no permission to retrieve the board.'
              }
              Token missing: {
                status: 403,
                message: 'Access forbidden - JWT token missing.'
              }
              Token invalid: {
                status: 403,
                message: 'Access forbidden - JWT token corrupted.'
              }
              Token expired: {
                status: 403,
                message: 'Access forbidden - JWT token expired.'
              }
        """
        pass

    def patch(self, board_id):
        """
        Change the name or visibility of the board.
        ---
        description: Changes the properties of board, if user has permissions to do it.
                     Only name and visibility can be changed - extra fields are ignored.
                     Requires a JWT token in Authorization header.
        tags:
          - board
        security:
          -
        parameters:
          - in: path
            name: board_id
            type: integer
            required: true
            description: ID of the board.
          - in: body
            name: body
            description: The only fields taken in consideration are name and visibility. Extra fields are ignored.
                         If no fields are present, the board is not modified.
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
          200:
            description: Board modified successfully. Returns the modified board.
            schema:
              $ref: '#/definitions/Board'
          404:
            description: Returned when no board with given id exists.
            schema:
              $ref: '#/definitions/Error'
            examples:
              No board: {
                status: 404,
                message: 'Not found - board with id 1 does not exist.'
              }
          403:
            description: Returned when user has no permissions to modify the board
                         or when JWT token is not present or is invalid.
            schema:
              $ref: '#/definitions/Error'
            examples:
              No permission: {
                status: 403,
                message: 'Access forbidden - no permission to modify the board.'
              }
              Token missing: {
                status: 403,
                message: 'Access forbidden - JWT token missing.'
              }
              Token invalid: {
                status: 403,
                message: 'Access forbidden - JWT token corrupted.'
              }
              Token expired: {
                status: 403,
                message: 'Access forbidden - JWT token expired.'
              }
        """

    def delete(self, board_id):
        """
        Delete the board.
        ---
        description: Deletes the board, if user has permissions to do it.
                     All the tasks and columns in the board are also deleted.
                     Requires a JWT token in Authorization header.
        tags:
          - board
        security:
          -
        parameters:
          - in: path
            name: board_id
            type: integer
            required: true
            description: ID of the board.
        responses:
          204:
            description: Returned on successful deletion of the board. The response has no body.
          404:
            description: Returned when no board with given id exists.
            schema:
              $ref: '#/definitions/Error'
            examples:
              No board: {
                status: 404,
                message: 'Not found - board with id 1 does not exist.'
              }
          403:
            description: Returned when user has no permissions to delete the board
                         or when JWT token is not present or is invalid.
            schema:
              $ref: '#/definitions/Error'
            examples:
              No permission: {
                status: 403,
                message: 'Access forbidden - no permission to delete the board.'
              }
              Token missing: {
                status: 403,
                message: 'Access forbidden - JWT token missing.'
              }
              Token invalid: {
                status: 403,
                message: 'Access forbidden - JWT token corrupted.'
              }
              Token expired: {
                status: 403,
                message: 'Access forbidden - JWT token expired.'
              }
        """


class Column(Resource):
    def get(self):
        """
        Retrieve the column.
        ---
        description: Returns column with given id, if user requesting it has permissions to do it.
                     Requires a JWT token in Authorization header.
        tags:
          - column
        security:
          -
        parameters:
          - in: query
            name: board_id
            type: integer
            required: true
            description: ID of the board.
          - in: query
            name: column_id
            type: integer
            required: true
            description: ID of the column.
        responses:
          200:
            description: Column successfully retrieved.
            schema:
              $ref: '#/definitions/Column'
          403:
            description: Returned when user has no permissions to retrieve the column
                         or when JWT token is not present or is invalid.
            schema:
              $ref: '#/definitions/Error'
            examples:
              No permission: {
                status: 403,
                message: 'Access forbidden - no permission to retrieve the column.'
              }
              Token missing: {
                status: 403,
                message: 'Access forbidden - JWT token missing.'
              }
              Token invalid: {
                status: 403,
                message: 'Access forbidden - JWT token corrupted.'
              }
              Token expired: {
                status: 403,
                message: 'Access forbidden - JWT token expired.'
              }
          404:
            description: Returned when no board or column with given id exists.
            schema:
              $ref: '#/definitions/Error'
            examples:
              No board: {
                status: 404,
                message: 'Not found - board with id 1 does not exist.'
              }
              No column: {
                status: 404,
                message: 'Not found - column with id 1 does not exist.'
              }
        """
        pass

    def delete(self):
        """
        Delete the column.
        ---
        description: Deletes the column, if user has permissions to do it.
                     All the tasks in the column are also deleted.
                     Requires a JWT token in Authorization header.
        tags:
          - column
        security:
          -
        parameters:
          - in: query
            name: board_id
            type: integer
            required: true
            description: ID of the board.
          - in: query
            name: column_id
            type: integer
            required: true
            description: ID of the column.
        responses:
          204:
            description: Column successfully deleted. The response has no body.
          403:
            description: Returned when user has no permissions to delete the column
                         or when JWT token is not present or is invalid.
            schema:
              $ref: '#/definitions/Error'
            examples:
              No permission: {
                status: 403,
                message: 'Access forbidden - no permission to delete the column.'
              }
              Token missing: {
                status: 403,
                message: 'Access forbidden - JWT token missing.'
              }
              Token invalid: {
                status: 403,
                message: 'Access forbidden - JWT token corrupted.'
              }
              Token expired: {
                status: 403,
                message: 'Access forbidden - JWT token expired.'
              }
          404:
            description: Returned when no board or column with given id exists.
            schema:
              $ref: '#/definitions/Error'
            examples:
              No board: {
                status: 404,
                message: 'Not found - board with id 1 does not exist.'
              }
              No column: {
                status: 404,
                message: 'Not found - column with id 1 does not exist.'
              }
        """
        pass

    def patch(self):
        """
        Change the name of the column.
        ---
        description: Changes the properties of the column, if user has permissions to do it.
                     Only name can be changed - extra fields are ignored.
                     Requires a JWT token in Authorization header.
        tags:
          - column
        security:
          -
        parameters:
          - in: query
            name: board_id
            type: integer
            required: true
            description: ID of the board.
          - in: query
            name: column_id
            type: integer
            required: true
            description: ID of the column.
          - in: body
            name: body
            required: true
            description: The only field taken in consideration is name. Extra fields are ignored.
                         If no fields are present, the column is not modified.
            schema:
              properties:
                name:
                  type: string
                  example: Done
        responses:
        responses:
          200:
            description: Column modified successfully. Returns the modified column.
            schema:
              $ref: '#/definitions/Column'
          404:
            description: Returned when no board or column with given id exists.
            schema:
              $ref: '#/definitions/Error'
            examples:
              No board: {
                status: 404,
                message: 'Not found - board with id 1 does not exist.'
              }
              No column: {
                status: 404,
                message: 'Not found - column with id 1 does not exist.'
              }
          403:
            description: Returned when user has no permissions to modify the column
                         or when JWT token is not present or is invalid.
            schema:
              $ref: '#/definitions/Error'
            examples:
              No permission: {
                status: 403,
                message: 'Access forbidden - no permission to modify the column.'
              }
              Token missing: {
                status: 403,
                message: 'Access forbidden - JWT token missing.'
              }
              Token invalid: {
                status: 403,
                message: 'Access forbidden - JWT token corrupted.'
              }
              Token expired: {
                status: 403,
                message: 'Access forbidden - JWT token expired.'
              }
        """
        pass


class Task(Resource):
    def get(self):
        """
        Retrieve the task.
        ---
        description: Returns task with given id, if user requesting it has permissions to do it.
                     Requires a JWT token in Authorization header.
        tags:
          - task
        security:
          -
        parameters:
          - in: query
            name: board_id
            type: integer
            required: true
            description: ID of the board.
          - in: query
            name: task_id
            type: integer
            required: true
            description: ID of the task.
        responses:
          200:
            description: Task successfully retrieved.
            schema:
              $ref: '#/definitions/Task'
          403:
            description: Returned when user has no permissions to retrieve the task
                         or when JWT token is not present or is invalid.
            schema:
              $ref: '#/definitions/Error'
            examples:
              No permission: {
                status: 403,
                message: 'Access forbidden - no permission to retrieve the task.'
              }
              Token missing: {
                status: 403,
                message: 'Access forbidden - JWT token missing.'
              }
              Token invalid: {
                status: 403,
                message: 'Access forbidden - JWT token corrupted.'
              }
              Token expired: {
                status: 403,
                message: 'Access forbidden - JWT token expired.'
              }
          404:
            description: Returned when no board or task with given id exists.
            schema:
              $ref: '#/definitions/Error'
            examples:
              No board: {
                status: 404,
                message: 'Not found - board with id 1 does not exist.'
              }
              No task: {
                status: 404,
                message: 'Not found - task with id 1 does not exist.'
              }
        """
        pass

    def delete(self):
        """
        Delete the task.
        ---
        description: Deletes the task, if user has permissions to do it.
                     Requires a JWT token in Authorization header.
        tags:
          - task
        security:
          -
        parameters:
          - in: query
            name: board_id
            type: integer
            required: true
            description: ID of the board.
          - in: query
            name: task_id
            type: integer
            required: true
            description: ID of the task.
        responses:
          204:
            description: Task successfully deleted. The response has no body.
          403:
            description: Returned when user has no permissions to delete the task
                         or when JWT token is not present or is invalid.
            schema:
              $ref: '#/definitions/Error'
            examples:
              No permission: {
                status: 403,
                message: 'Access forbidden - no permission to delete the task.'
              }
              Token missing: {
                status: 403,
                message: 'Access forbidden - JWT token missing.'
              }
              Token invalid: {
                status: 403,
                message: 'Access forbidden - JWT token corrupted.'
              }
              Token expired: {
                status: 403,
                message: 'Access forbidden - JWT token expired.'
              }
          404:
            description: Returned when no board or task with given id exists.
            schema:
              $ref: '#/definitions/Error'
            examples:
              No board: {
                status: 404,
                message: 'Not found - board with id 1 does not exist.'
              }
              No task: {
                status: 404,
                message: 'Not found - task with id 1 does not exist.'
              }
        """
        pass

    def patch(self):
        """
        Change the properties of the task.
        ---
        description: Changes the properties of the task, if user has permissions to do it.
                     Every field except id can be changed.
                     Requires a JWT token in Authorization header.
        tags:
          - task
        security:
          -
        parameters:
          - in: query
            name: board_id
            type: integer
            required: true
            description: ID of the board.
          - in: query
            name: task_id
            type: integer
            required: true
            description: ID of the task.
          - in: body
            name: body
            required: true
            description: The fields taken into consideration are "column_id", "description", "name" and "user_id".
                         Extra fields are ignored. User id and column id must be valid,
                         i. e. column must exist within the board and user with given id must have permissions
                         to be assigned to task.
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
          200:
            description: Task modified successfully. Returns the modified task.
            schema:
              $ref: '#/definitions/Task'
          404:
            description: Returned when no board or task with given id exists.
            schema:
              $ref: '#/definitions/Error'
            examples:
              No board: {
                status: 404,
                message: 'Not found - board with id 1 does not exist.'
              }
              No task: {
                status: 404,
                message: 'Not found - task with id 1 does not exist.'
              }
          403:
            description: Returned when user has no permissions to modify the task
                         or when JWT token is not present or is invalid.
            schema:
              $ref: '#/definitions/Error'
            examples:
              No permission: {
                status: 403,
                message: 'Access forbidden - no permission to modify the task.'
              }
              Token missing: {
                status: 403,
                message: 'Access forbidden - JWT token missing.'
              }
              Token invalid: {
                status: 403,
                message: 'Access forbidden - JWT token corrupted.'
              }
              Token expired: {
                status: 403,
                message: 'Access forbidden - JWT token expired.'
              }
          409:
            description: Returned when no column with given column_id exists, or user with given user_id
                         does not exist or is not permitted to be assigned to a task.
            schema:
              $ref: '#/definitions/Error'
            examples:
              No column: {
                status: 409,
                message: 'Invalid column id - column with id 1 does not exist.'
              }
              No user: {
                status: 409,
                message: 'Invalid user id - user with id 1 does not exist.'
              }
              Insufficient permissions for user: {
                status: 409,
                message: 'Insufficient permissions - user with id 1 cannot be assigned to a task.'
              }
        """
        pass
