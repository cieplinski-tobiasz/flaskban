"""
The module contains instanced of extensions
used by Flask application.

Attributes:
    API: Instance of Flask-RESTful extension.
    SWAGGER: Instance of Flasgger extension.
    DB: Instance of Flask-SQLAlchemy extension.
    JWT: Instance of Flask-JWT-Extended extension.
"""

from flasgger import Swagger
from flask_jwt_extended import JWTManager
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy

from config import TEMPLATE_FILENAME

API = Api()
SWAGGER = Swagger(template_file=TEMPLATE_FILENAME)
DB = SQLAlchemy()
JWT = JWTManager()
