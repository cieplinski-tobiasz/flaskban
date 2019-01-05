from flask_restful import Resource


class Permissions(Resource):
    def get(self):
        """
        List permissions.
        ---
        description: Returns a list of all permissions that can be assigned to a user within a board.
                     Assigned permissions must be present in the list, i.e. a permission
                     that is not listed on returned list cannot be assigned to any user.
                     Requires an authentication token in Authorization header.
        tags:
          - permission
        security:
          -
        responses:
          200:
            description: List of permissions.
            example: {
              permissions: [
                {id: 1, name: "COLUMN_CREATE", description: "Allows for creating columns."},
                {id: 2, name: "COLUMN_DELETE", description: "Allows for deleting columns."},
                {id: 3, name: "TASK_CREATE", description: "Allows for creating tasks."}
              ]
            }
          401:
            description: Returned when authentication token is missing or invalid.
            schema:
              $ref: '#/definitions/Error'
            examples:
              Invalid token: {
                status: 401,
                message: 'Unauthorized - no valid token present.'
              }
        """
        pass
