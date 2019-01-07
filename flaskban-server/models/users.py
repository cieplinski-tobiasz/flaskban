from flask_jwt_extended import create_access_token
from marshmallow import Schema, fields, post_load, validates_schema, ValidationError
from passlib.hash import pbkdf2_sha256
from sqlalchemy import exists
from sqlalchemy.ext.hybrid import hybrid_property

from common.errors import AlreadyExistsError, InvalidDataError, UnauthorizedError
from extensions import db


class User(db.Model):
    id_ = db.Column('id', db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    _password = db.Column(db.String(50), nullable=False)

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def password(self, plain):
        self._password = pbkdf2_sha256.hash(plain)

    @classmethod
    def find_by_name(cls, name):
        return cls.query.filter_by(name=name).first()

    @classmethod
    def find_by_email(cls, email):
        return cls.query.filter_by(email=email)

    def _already_saved(self, session):
        return session.query(
            exists().where(
                (User.name == self.name) | (User.email == self.email)
            )
        ).scalar()

    def save(self):
        if not self.name or not self._password or not self.email:
            raise InvalidDataError('Required fields are not present.')

        if self._already_saved(db.session):
            raise AlreadyExistsError('User already exists.')

        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return f'User(id={self.id_}, name={self.name}, email={self.email})'


class UserRegisterSchema(Schema):
    __model__ = User

    id_ = fields.Integer(attribute='id', dump_only=True)
    username = fields.Str(attribute='name', required=True)
    email = fields.Email(required=True)
    password = fields.Str(load_only=True, required=True)

    @post_load
    def make_user(self, data):
        return self.__model__(**data)


class UserLoginSchema(Schema):
    __model__ = User

    username = fields.Str(attribute='name')
    email = fields.Email()
    password = fields.Str(attribute='_password', load_only=True, required=True)

    @validates_schema
    def validate(self, data):
        if 'name' not in data and 'email' not in data:
            raise ValidationError('Either username or email must be present.')

    @post_load
    def make_user(self, data):
        return self.__model__(**data)


register_schema = UserRegisterSchema()
login_schema = UserLoginSchema()


def register(user):
    user.save()


def login(user):
    db_user = User.find_by_name(user.name) if user.name else User.find_by_email(user.email)

    if not db_user or not pbkdf2_sha256.verify(user.password, db_user.password):
        raise UnauthorizedError('Wrong username or password.')

    return create_access_token(identity=db_user.id_)
