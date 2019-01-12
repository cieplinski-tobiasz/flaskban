from flask_restful import Api
from flasgger import Swagger
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

API = Api()
SWAGGER = Swagger()
DB = SQLAlchemy()
JWT = JWTManager()
