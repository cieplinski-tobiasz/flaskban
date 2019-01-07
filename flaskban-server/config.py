class Config:
    SWAGGER = {
        'title': 'FlaskBan',
        'uiversion': 3,
    }


class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
