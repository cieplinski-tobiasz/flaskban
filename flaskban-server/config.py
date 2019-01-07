class Config:
    SWAGGER = {
        'title': 'FlaskBan',
        'uiversion': 3,
    }


class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = 'super-secret-developer-key'


def get_config(name):
    if name == 'dev':
        return DevelopmentConfig()

    raise ValueError(f'No config named {name}')
