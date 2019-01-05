from resources.auth import Login, Register
from resources.collections import *
from resources.entities import *
from resources.perms import *

from flask import Flask
from flask_restful import Api
from flasgger import Swagger

app = Flask(__name__)
api = Api(app)
app.config['SWAGGER'] = {
    'title': 'FlaskBan',
    'uiversion': 3,
}
swag = Swagger(app)

api.add_resource(Login, '/auth/login')
api.add_resource(Register, '/auth/register')

api.add_resource(Boards, '/boards')
api.add_resource(Board, '/boards/<int:board_id>')

api.add_resource(Columns, '/boards/<int:board_id>/columns')
api.add_resource(Column, '/boards/<int:board_id>/columns/<int:column_id>')

api.add_resource(Tasks, '/boards/<int:board_id>/tasks')
api.add_resource(Task, '/boards/<int:board_id>/tasks/<int:task_id>')

api.add_resource(Permissions, '/permissions')

if __name__ == '__main__':
    app.run()
