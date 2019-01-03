from flask_restful import Resource


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
              properties:
                token:
                  type: string
                  required: true
                  example: eyJh.eyJzdWIiOiIxMjM0NTY3ODkaW4iOnRydWV9.TJVA95OrM7E2cBab30RMHrHDcEfxjoYZg
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
              failure: {status: 401, message: "Unauthorized - wrong username or password."}
        """
        pass


class Register(Resource):
    def post(self):
        # TODO [DOCS]: account with given email or username already exists
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
              properties:
                token:
                  type: string
                  required: true
        """
        pass
