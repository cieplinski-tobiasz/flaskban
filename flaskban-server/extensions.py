from flasgger import Swagger
from flask_jwt_extended import JWTManager
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy

from config import TEMPLATE_FILENAME

API = Api()
SWAGGER = Swagger(template_file=TEMPLATE_FILENAME)
DB = SQLAlchemy()
JWT = JWTManager()
