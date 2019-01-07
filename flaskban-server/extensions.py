from flask_restful import Api
from flasgger import Swagger
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

api = Api()
swagger = Swagger()
db = SQLAlchemy()
jwt = JWTManager()
