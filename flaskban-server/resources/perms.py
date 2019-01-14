from flask_restful import Resource


class Permissions(Resource):
    def get(self):
        """
        List permissions.
        ---
        description: Returns a list of all permissions
                     that can be assigned to a user within a board.
                     Assigned permissions must be present in the list,
                     i.e. a permission that is not listed on returned list
                     cannot be assigned to any user.
                     Requires an authentication token in Authorization header.
        tags:
          - permission
        security:
          - authBearer: []
        responses:
          '200':
            description: List of permissions.
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/PermissionList'
          '401':
            $ref: '#/components/responses/NoToken'
        """


class UserPermissions(Resource):
    def get(self):
        """
        List permissions of a user.
        ---
        description: Returns a list of permissions granted to user within the board,
                     if the user requesting it has permissions to list them.
                     Requires an authentication token in Authorization header.
        tags:
          - permission
        security:
          - authBearer: []
        parameters:
          - in: path
            schema:
              type: integer
            name: board_id
            required: true
            description: ID of the board.
          - in: path
            schema:
              type: integer
            name: user_id
            required: true
            description: ID of the user.
        responses:
          '200':
            description: List of permissions.
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/PermissionList'
          '401':
            $ref: '#/components/responses/NoToken'
          '403':
            description: Returned when user has no permissions to list the permissions.
            content:
              application/json:
                schema:
                  $ref: '#/definitions/Error'
            examples:
              No permission:
                status: 403
                message: Forbidden - no permission to list the permissions
          '404':
            description: Returned when no board or user with given id exists.
            content:
              application/json:
                schema:
                  $ref: '#/definitions/Error'
            examples:
              No board:
                status: 404
                message: Not found - board with id 1 does not exist
              No user:
                status: 404
                message: Not found - user with id 1 does not exist
        """

    def put(self):
        """
        Replace permissions of user.
        ---
        description: Assigns permissions for given user within the board,
                     if the user requesting it has permissions to do it.
                     If user had any permissions assigned earlier, they will be overwritten.
                     Permissions must be valid, i.e. must be present
                     in the list returned by /permissions GET endpoint.
                     Requires an authentication token in Authorization header.
        tags:
          - permission
        security:
          - bearerAuth: []
        parameters:
          - in: path
            schema:
              type: integer
            name: board_id
            required: true
            description: ID of the board.
          - in: path
            schema:
              type: integer
            name: user_id
            required: true
            description: ID of the user.
        requestBody:
          description: List of permission names.
          required: true
          content:
            application/json:
              schema:
                properties:
                  permissions:
                    type: array
                    items: string
                    required: true
                    example: [COLUMN_CREATE, BOARD_VIEW]
        responses:
          '204':
            description: Permissions successfully assigned. The response has no body.
          '401':
            $ref: '#/components/responses/NoToken'
          '403':
            description: Returned when user has no permissions to assign permissions.
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/Error'
            examples:
              No permission:
                status: 403
                message: Forbidden - no permission to assign the permissions
          '404':
            description: Returned when no board or user with given id exists.
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/Error'
            examples:
              No board:
                status: 404
                message: Board with id 1 does not exist
              No user:
                status: 404
                message: User with id 1 does not exist
          '409':
            description: Returned when list of permissions contains nonexistent ids.
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/Error'
            examples:
              Invalid permissions:
                status: 409
                message: Conflict - permissions with names [COL_CR] do not exist
        """

    def delete(self):
        """
        Delete permissions of user.
        ---
        description: Deletes all permissions for given user within the board,
                     if the user requesting it has permissions to do it.
                     Requires an authentication token in Authorization header.
        tags:
          - permission
        security:
          - authBearer: []
        parameters:
          - in: path
            schema:
              type: integer
            name: board_id
            required: true
            description: ID of the board.
          - in: path
            schema:
              type: integer
            name: user_id
            required: true
            description: ID of the user.
        responses:
          '204':
            description: Permissions successfully deleted. The response has no body.
          '401':
            $ref: '#/components/responses/NoToken'
          '403':
            description: Returned when user has no permissions to delete permissions.
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/Error'
            examples:
              No permission:
                status: 403
                message: Forbidden - no permission to delete the permissions
          '404':
            description: Returned when no board or user with
                         given id exists, or when user has no permissions assigned.
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/Error'
            examples:
              No board:
                status: 404
                message: Not found - board with id 1 does not exist
              No user:
                status: 404
                message: Not found - user with id 1 does not exist
              No permissions:
                status: 404
                message: Not found - user with id 1 has no permissions assigned
        """
