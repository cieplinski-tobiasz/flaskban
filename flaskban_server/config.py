"""
The module contains objects and dictionaries
used for configuring the application.

Attributes:
    TEMPLATE_FILENAME (str): Name of the file passed to Swagger __init__ method.
"""


class Config:
    """
    Base class used for common configuration properties.

    Properties:
        SWAGGER (dict): Config of Flasgger extension.
    """
    SWAGGER = {
        'title': 'FlaskBan',
        'uiversion': 3,
    }


class DevelopmentConfig(Config):
    """
    Config used for development.

    Properties:
        SQLALCHEMY_DATABASE_URI (str): Address of the database server.
        SQLALCHEMY_TRACK_MODIFICATIONS (bool): Configuration flag for SQLAlchemy.
        JWT_SECRET_KEY (str): Key used for signing JWT tokens.
    """
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = 'super-secret-developer-key'


def get_config(name):
    """
    Returns config based on the name of it.

    Args:
        name (str): Name of the config.

    Returns:
        Config object.

    Raises:
        ValueError: If no config with given name exists.
    """
    if name == 'dev':
        return DevelopmentConfig()

    raise ValueError(f'No config named {name}')


TEMPLATE_FILENAME = 'swagger_docs.yml'
