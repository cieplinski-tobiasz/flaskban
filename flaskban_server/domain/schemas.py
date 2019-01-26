"""
The model contains schemas
for all domain specific objects
used for validation and serialization.
"""

from marshmallow import Schema, fields, validates_schema, post_load, ValidationError
from marshmallow_enum import EnumField

import domain.models


class UserRegisterSchema(Schema):
    """
    Defines a validation schema for user used for registration and for serialization.

    Properties:
        id_: Integer datatype. Used only in response and assigned by the database.
        username: String datatype. Must be present for validation to succeed.
        email: Email datatype. Must be present and valid for validation to succeed.
        password: String datatype. Must be present for validation to succeed.
    """
    __model__ = domain.models.User

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
    Defines a schema for user used for validating login data and serialization.

    The schema requires that either `username` or `email` field is present.

    Properties:
        username: String datatype.
        email: Email datatype.
        password: String datatype. Must be present for validation to succeed.
                  The field is never serialized.

    """
    __model__ = domain.models.User

    username = fields.Str(attribute='name')
    email = fields.Email()
    password = fields.Str(attribute='_password', load_only=True, required=True)

    @validates_schema
    def validate(self, data, many=None, partial=None):
        """
        Checks if either `name` or `email` is present in the `data` dictionary.

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


class TaskSchema(Schema):
    """
    Defines a validation and serialization schema for task.
    """
    __model__ = domain.models.Task

    id_ = fields.Integer(data_key='id', dump_only=True)
    name = fields.Str(required=True)
    description = fields.Str()
    column_id = fields.Integer(required=True)
    user_id = fields.Integer()

    @post_load
    def make_task(self, data):
        """
        Creates task object from dictionary.

        Args:
            data (dict): Dictionary containing the input fields.

        Returns:
            Task object with filled fields according to `data`.
        """
        return self.__model__(**data)


class ColumnSchema(Schema):
    """
    Defines a validation and serialization schema for column.
    """
    __model__ = domain.models.Column

    id_ = fields.Integer(data_key='id', dump_only=True)
    name = fields.Str(required=True)
    tasks = fields.Nested(TaskSchema, many=True, dump_only=True)

    @post_load
    def make_column(self, data):
        """
        Creates column object from dictionary.

        Args:
            data (dict): Dictionary containing the input fields.

        Returns:
            Column object with filled fields according to `data`.
        """
        return self.__model__(**data)


class BoardSchema(Schema):
    """
    Defines a validation and serialization schema for board.
    """
    __model__ = domain.models.Board

    id_ = fields.Integer(data_key='id', dump_only=True)
    name = fields.Str(required=True)
    visibility = EnumField(domain.models.Visibility, required=True)
    columns = fields.Nested(ColumnSchema, many=True, dump_only=True)

    @post_load
    def make_board(self, data):
        """
        Creates board object from dictionary.

        Args:
            data (dict): Dictionary containing the input fields.

        Returns:
            Board object with filled fields according to `data`.
        """
        return self.__model__(**data)


BOARD_SCHEMA = BoardSchema()
COLUMN_SCHEMA = ColumnSchema()
TASK_SCHEMA = TaskSchema()
LOGIN_SCHEMA = UserLoginSchema()
REGISTER_SCHEMA = UserRegisterSchema()
