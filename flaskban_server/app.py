"""
The module contains functions related to
initializing the application.
"""
from flask import Flask

from config import get_config

from extensions import API, DB, SWAGGER, JWT

from resources.auth import Login, Register
from resources.collections import Boards, Columns, Tasks
from resources.entities import Board, Column, Task
from resources.perms import Permissions, UserPermissions


def _init_extensions(app, *exts):
    """
    Calls init_app on app for every extension passed to the method.

    Args:
        app (Flask): Instance of Flask class.
        exts: List of extensions to be applied.
    """
    for ext in exts:
        ext.init_app(app)


def create_app(config_name):
    """
    Initializes the application.

    The function adds resources to the REST API
    and initializes all the required extensions.

    If the function is called with `config_name` equal to 'dev',
    the database will be dropped and recreated.

    Args:
        config_name (str): Name of the configuration.
                           Currently only 'dev' name is supported.
    """
    app = Flask(__name__)
    app.config.from_object(get_config(config_name))

    API.add_resource(Login, '/auth/login')
    API.add_resource(Register, '/auth/register')

    API.add_resource(Boards, '/boards')
    API.add_resource(Board, '/boards/<int:board_id>')

    API.add_resource(Columns, '/boards/<int:board_id>/columns')
    API.add_resource(Column, '/boards/<int:board_id>/columns/<int:column_id>')

    API.add_resource(Tasks, '/boards/<int:board_id>/tasks')
    API.add_resource(Task, '/boards/<int:board_id>/tasks/<int:task_id>')

    API.add_resource(Permissions, '/permissions')
    API.add_resource(UserPermissions, '/boards/<int:board_id>/permissions/<int:user_id>')

    _init_extensions(app, API, SWAGGER, DB, JWT)

    if config_name == 'dev':
        DB.drop_all(app=app)
        DB.create_all(app=app)

    return app
