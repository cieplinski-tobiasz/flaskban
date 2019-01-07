from flask_restful import Api
from flasgger import Swagger
from flask_sqlalchemy import SQLAlchemy

api = Api()
swagger = Swagger()
db = SQLAlchemy()
