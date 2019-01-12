"""
The module contains the User model, validation schema
and functions allowing for creation of user and token retrieval.

Attributes:
    REGISTER_SCHEMA: Schema used for validating the input before registration and for serialization.
    LOGIN_SCHEMA: Schema used for validating the input before login and for serialization.
"""

from flask_jwt_extended import create_access_token
from marshmallow import Schema, fields, post_load, validates_schema, ValidationError
from passlib.hash import pbkdf2_sha256
from sqlalchemy import exists
from sqlalchemy.ext.hybrid import hybrid_property

from errors import AlreadyExistsError, InvalidDataError, UnauthorizedError
from extensions import DB


class User(DB.Model):
    """
    Defines an ORM model for user.

    If the __init__ method is called with the `password` keyword argument,
    the password will be automatically hashed. However, if it will be called
    with `_password` keyword argument, the password *will not* be hashed.
    It *must* be taken into consideration, because invalid use of the __init__ method
    may cause security issues.

    Attributes:
        id_ (int): ID of the user.
        name (str): Username.
        email (str): Email of the user.
    """
    id_ = DB.Column('id', DB.Integer, primary_key=True)
    name = DB.Column(DB.String(30), unique=True, nullable=False)
    email = DB.Column(DB.String(50), unique=True, nullable=False)
    _password = DB.Column(DB.String(50), nullable=False)

    @hybrid_property
    def password(self):
        """
        str: Password of the user.

        The password may be hashed or not hashed,
        depending on how the __init__ method was called.
        The `password` setter hashes the password before assigning it to the property.
        """
        return self._password

    @password.setter
    def password(self, plain):
        self._password = pbkdf2_sha256.hash(plain)

    @classmethod
    def find_by_name(cls, name):
        """
        Queries the database for a user with given name.

        Args:
            name (str): The name of the user.

        Returns:
            User if user with given name exists, None otherwise.
        """
        return cls.query.filter_by(name=name).first()

    @classmethod
    def find_by_email(cls, email):
        """
        Queries the database for a user with given email.

        Args:
            email (str): The email of the user.

        Returns:
            User if user with given email exists, None otherwise.
        """
        return cls.query.filter_by(email=email)

    def _already_saved(self, session):
        """
        Queries the database to check if user with given name or email
        has already been stored.

        Args:
            session: Active session with database.

        Returns:
            True if user already exists, False otherwise.
        """
        return session.query(
            exists().where(
                (User.name == self.name) | (User.email == self.email)
            )
        ).scalar()

    def save(self):
        """
        Stores the user in the database.

        Raises:
            InvalidDataError: If any of the fields in model is not present.
            AlreadyExistsError: If user with given name or email already exists.
        """
        if not self.name or not self._password or not self.email:
            raise InvalidDataError('Required fields are not present')

        if self._already_saved(DB.session):
            raise AlreadyExistsError('User already exists')

        DB.session.add(self)
        DB.session.commit()

    def __repr__(self):
        return f'User(id={self.id_}, name={self.name}, email={self.email})'


class UserRegisterSchema(Schema):
    """
    Defines a validation schema for user used for registration and for serialization.

    Properties:
        id_: Integer datatype. Used only in response and assigned by the database.
        username: String datatype. Must be present for validation to succeed.
        email: Email datatype. Must be present and valid for validation to succeed.
        password: String datatype. Must be present for validation to succeed.
    """
    __model__ = User

    id_ = fields.Integer(attribute='id', dump_only=True)
    username = fields.Str(attribute='name', required=True)
    email = fields.Email(required=True)
    password = fields.Str(load_only=True, required=True)

    @post_load
    def make_user(self, data):
        """
        Creates user object from dictionary.

        Args:
            data (dict): Dictionary containing the input fields.

        Returns:
            User object with filled fields according to `data`.
        """
        return self.__model__(**data)


class UserLoginSchema(Schema):
    """
    Defines a validation schema for user used for login and serialization.

    The schema requires that either `username` or `email` field is present.

    Properties:
        username: String datatype.
        email: Email datatype.
        password: String datatype. Must be present for validation to succeed.
                  The field is never serialized.

    """
    __model__ = User

    username = fields.Str(attribute='name')
    email = fields.Email()
    password = fields.Str(attribute='_password', load_only=True, required=True)

    @validates_schema
    def validate(self, data, many=None, partial=None):
        """
        Checks if either `name` or `email` is present
        in the `data` dictionary.

        Args:
            data (dict): Dictionary containing the input fields.
            many: Not used, present for overriding the original method.
            partial: Not used, present for overriding the original method.

        Raises:
            ValidationError: If `name` and `email` fields are not present.
        """
        if 'name' not in data and 'email' not in data:
            raise ValidationError('Either username or email must be present')

    @post_load
    def make_user(self, data):
        """
        Creates user object from dictionary.

        Args:
            data (dict): Dictionary containing the input fields.

        Returns:
            User object with filled fields according to `data`.
        """
        return self.__model__(**data)


def register(user):
    """
    Calls user's `save()` method.

    Works as a simple delegation function.
    If anything should be checked before registration in the future,
    it should be checked in this function.

    Args:
        user (User)
    """
    user.save()


def login(user):
    """
    Searches for the user in the database and returns the token,
    given the credentials are correct.

    If the `user` object has both `name` and `email` fields,
    the `name` field is used first for searching the database.
    At least one of these fields *must* be present.

    Args:
        user (User)

    Returns:
        token (str): Authorization token.

    Raises:
        UnauthorizedError: If user does not exist or password is not correct.
    """
    db_user = User.find_by_name(user.name) if user.name else User.find_by_email(user.email)

    if not db_user or not pbkdf2_sha256.verify(user.password, db_user.password):
        raise UnauthorizedError('Wrong username or password')

    return create_access_token(identity=db_user.id_)


REGISTER_SCHEMA = UserRegisterSchema()
LOGIN_SCHEMA = UserLoginSchema()
