import config
from extensions import api, swagger

from resources.auth import Login, Register
from resources.collections import Boards, Columns, Tasks
from resources.entities import Board, Column, Task
from resources.perms import Permissions, UserPermissions

from flask import Flask


def create_app():
    app = Flask(__name__)
    app.config.from_object(config.DevelopmentConfig)

    swagger.init_app(app)

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

    api.init_app(app)

    return app




