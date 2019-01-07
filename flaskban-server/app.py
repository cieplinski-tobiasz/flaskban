import config

from resources.auth import Login, Register
from resources.collections import Boards, Columns, Tasks
from resources.entities import Board, Column, Task
from resources.perms import Permissions, UserPermissions

from flask import Flask
from flask_restful import Api
from flasgger import Swagger

app = Flask(__name__)
app.config.from_object(config.DevelopmentConfig)

swag = Swagger(app)

api = Api(app)

api.add_resource(Login, '/auth/login')
api.add_resource(Register, '/auth/register')

api.add_resource(Boards, '/boards')
api.add_resource(Board, '/boards/<int:board_id>')

api.add_resource(Columns, '/boards/<int:board_id>/columns')
api.add_resource(Column, '/boards/<int:board_id>/columns/<int:column_id>')

api.add_resource(Tasks, '/boards/<int:board_id>/tasks')
api.add_resource(Task, '/boards/<int:board_id>/tasks/<int:task_id>')

api.add_resource(Permissions, '/permissions')
api.add_resource(UserPermissions, '/boards/<int:board_id>/permissions/<int:user_id>')

if __name__ == '__main__':
    app.run()
