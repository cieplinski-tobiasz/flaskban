from flask_restful import Resource


class Boards(Resource):
    def get(self):
        """
        List public boards.
        ---
        description: Returns a list of boards. The list does not include private boards.
        tags:
          - board
        parameters:
          - in: query
            type: integer
            name: offset
            default: 0
            description: Index of first returned board from all search results.
          - in: query
            type: integer
            name: limit
            default: 20
            description: Maximum number of results returned (acceptable values are 1 to 1000).
        responses:
          200:
            description: List of boards.
            schema:
              id: BoardList
              properties:
                boards:
                  type: list
                  required: true
                  example: [
                    {id: 1, name: "My Wednesday plan", visibility: public, columns: []},
                    {id: 2, name: "Christmas preparation", visibility: public, columns: [
                      {id: 1, name: "To do", tasks: [
                        {id: 1, column_id: 1, user_id: 3, name: 'Dress the Christmas tree'}
                      ]}
                    ]}
                  ]
        """
        pass

    def post(self):
        """
        Create new board.
        ---
        description: Creates a new, empty kanban board and makes the user who created it an administrator of the board.
                     Private boards cannot be seen by people without access, while public boards may be seen by anybody.
                     Requires a JWT Token in Authorization header.
        tags:
          - board
        security:
          -
        parameters:
          - in: body
            name: body
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
        responses:
          201:
            description: Board created successfully. Returns the location of newly created board in header,
                         and the object in response body.
            headers:
              Location:
                type: string
                format: uri
                example: /boards/1
                description: Location of newly created board.
            schema:
              id: Board
              properties:
                id:
                  type: integer
                  required: true
                  example: 1
                name:
                  type: string
                  required: true
                  example: My Wednesday Plan
                visibility:
                  type: string
                  required: true
                  enum: [public, private]
                  example: private
                columns:
                  type: list
                  required: true
                  example: []
          403:
            description: Returned when JWT token is not present or is invalid.
            schema:
              $ref: '#/definitions/Error'
            examples:
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


class Columns(Resource):
    def get(self):
        """
        List columns.
        ---
        description: Returns a list of columns for board with given id, if user requesting it has permissions to do it.
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
        responses:
          200:
            description: List of columns.
            schema:
              id: ColumnList
              properties:
                columns:
                  type: list
                  required: true
                  example: [
                    {id: 1, name: "To do", tasks: []},
                    {id: 2, name: "In progress", tasks: [
                      {id: 1, column_id: 2, name: "JWT generation", description: "Authentication feature.", user_id: 4}
                    ]}
                  ]
          403:
            description: Returned when user has no permissions to list the columns
                         or when JWT token is not present or is invalid.
            schema:
              $ref: '#/definitions/Error'
            examples:
              No permission: {
                status: 403,
                message: 'Access forbidden - no permission to list the columns.'
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
            description: Returned when no board with given id exists.
            schema:
              $ref: '#/definitions/Error'
            examples:
              No board: {
                status: 404,
                message: 'Not found - board with id 1 does not exist.'
              }
        """
        pass

    def post(self):
        """
        Create new column.
        ---
        description: Creates a new column in the board, if user has the permissions to do it.
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
          - in: body
            name: body
            required: true
            description: The name of the column is required, and it has to be unique within the board.
            schema:
              properties:
                name:
                  type: string
                  required: true
                  example: To do
        responses:
          201:
            description: Column successfully created. Returns the location of newly created column in header,
                         and the object in response body.
            headers:
              Location:
                type: string
                format: uri
                example: /boards/1/columns/1
                description: Location of newly created column.
            schema:
              id: Column
              properties:
                id:
                  type: integer
                  required: true
                  example: 1
                name:
                  type: string
                  required: true
                  example: To do
                tasks:
                  type: list
                  required: true
                  example: []
          403:
            description: Returned when user has no permissions to create the column
                         or when JWT token is not present or is invalid.
            schema:
              $ref: '#/definitions/Error'
            examples:
              No permission: {
                status: 403,
                message: 'Access forbidden - no permission to create the column.'
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
            description: Returned when no board with given id exists.
            schema:
              $ref: '#/definitions/Error'
            examples:
              No board: {
                status: 404,
                message: 'Not found - board with id 1 does not exist.'
              }
          409:
            description: Returned when column with given name already exists.
            schema:
              $ref: '#/definitions/Error'
            examples:
              Column already exists: {
                status: 409,
                message: 'Column creation failed - column with a given name already exists.'
              }
        """
        pass


class Tasks(Resource):
    def get(self):
        """
        List tasks.
        ---
        description: Returns a list of tasks for board with given id, if user requesting it has permissions to do it.
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
        responses:
          200:
            description: List of tasks.
            schema:
              id: TaskList
              properties:
                tasks:
                  type: list
                  required: true
                  example: [
                    {id: 1, column_id: 2, name: "JWT generation", description: "Authentication feature.", user_id: 4},
                    {id: 2, column_id: 1, name: "Finish the docs"}
                  ]
          403:
            description: Returned when user has no permissions to list the tasks
                         or when JWT token is not present or is invalid.
            schema:
              $ref: '#/definitions/Error'
            examples:
              No permission: {
                status: 403,
                message: 'Access forbidden - no permission to list the tasks.'
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
            description: Returned when no board with given id exists.
            schema:
              $ref: '#/definitions/Error'
            examples:
              No board: {
                status: 404,
                message: 'Not found - board with id 1 does not exist.'
              }
        """
        pass

    def post(self):
        """
        Create new task.
        ---
        description: Creates new task if the user has the permissions to do it.
                     Task is associated with board and column, i.e. task can belong to *one* column only,
                     and to *one* board only.
                     Requires a JWT token in Authorization header.
        tags:
          - task
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
            required: true
            description: The name of the task is required. User with given ID must be permitted by the board
                         to be able to be assigned to a given task. Task's name must be unique within the column.
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
                  description: ID of column that the task is assigned to. ID must be valid, i.e. a column with given id
                               must exist within the board.
                user_id:
                  type: integer
                  example: 4
                  description: ID of the user responsible for the task. The board must assign permissions for the user
                               with given ID that allow him to be assigned to the task.
        responses:
          201:
            description: Task successfully created. Returns the location of newly created task in header,
                         and the object in response body.
            headers:
              Location:
                type: string
                format: uri
                example: /boards/1/tasks/1
                description: Location of newly created task.
            schema:
              id: Task
              properties:
                id:
                  type: integer
                  required: true
                  example: 1
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
                user_id:
                  type: integer
                  example: 4
          403:
            description: Returned when user has no permissions to create the task
                         or when JWT token is not present or is invalid.
            schema:
              $ref: '#/definitions/Error'
            examples:
              No permission: {
                status: 403,
                message: 'Access forbidden - no permission to create the task.'
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
            description: Returned when no board with given id exists.
            schema:
              $ref: '#/definitions/Error'
            examples:
              No board: {
                status: 404,
                message: 'Not found - board with id 1 does not exist.'
              }
          409:
            description: Returned when task with given name already exists within the column.
            schema:
              $ref: '#/definitions/Error'
            examples:
              Task already exists: {
                status: 409,
                message: 'Task creation failed - task with a given name already exists within column with id 1.'
              }
        """
        pass
