"""
The module contains the Board model, validation schema,
Visibility enum.

Attributes:
    BOARD_SCHEMA: Schema used for validating the input and serialization.
"""
from enum import Enum

from marshmallow import Schema, fields, post_load
from marshmallow_enum import EnumField

from sqlalchemy import exists

from errors import InvalidDataError, NotFoundError
from extensions import DB


class Visibility(Enum):
    """
    Defines the possible values for visibility of the board.
    If the board is private, it may be seen only be people with proper permissions.
    If the board is public, it may be seen by anybody.

    Properties:
        private (int)
        public (int)
    """
    private = 1
    public = 2


class Board(DB.Model):
    """
    Defines the ORM model for kanban board.

    Attributes:
        id_ (int): ID of the board.
        name (str): Name of the board.
        visibility (enum): Visibility of the board.

    """
    id_ = DB.Column('id', DB.Integer, primary_key=True)
    name = DB.Column(DB.String(), nullable=False)
    visibility = DB.Column(DB.Enum(Visibility), nullable=False)

    @classmethod
    def exists_by_id(cls, id_):
        """
        Queries the database to check if board with given id
        has already been stored.

        Args:
            id_: ID of the board.

        Returns:
            True if board exists, False otherwise.
        """
        return cls.query.filter(exists().where(cls.id_ == id_)).scalar()

    @classmethod
    def find_by_name(cls, name):
        """
        Queries the database for a board with given name.

        Args:
            name (str): The name of the board.

        Returns:
            Board if board with given name exists, None otherwise.
        """
        return cls.query.filter_by(name=name).first()

    def save(self):
        """
        Stores the board in the database.

        Raises:
            InvalidDataError: If any of the fields in model is not present.
        """
        if not self.name or not self.visibility:
            raise InvalidDataError('Required fields are not present')

        DB.session.add(self)
        DB.session.commit()

    @classmethod
    def delete(cls, id_):
        """
        Deletes the board with given id from the database.

        All the columns and tasks associated with the board are also deleted.

        Args:
            id_ (int): ID of the board.

        Raises:
            NotFoundError: If board with given id does not exist.
        """
        if not cls.exists_by_id(id_):
            raise NotFoundError(f'Board with id {id_} does not exist')

        board = cls.query.filter_by(id_=id_).one()
        DB.session.delete(board)
        DB.session.commit()

    def __repr__(self):
        return f'Board(id={self.id_}, name={self.name}, visibility={self.visibility.name})'


class BoardSchema(Schema):
    """
    Defines a validation and serialization schema for board.
    """
    __model__ = Board

    id_ = fields.Integer(data_key='id', dump_only=True)
    name = fields.Str(required=True)
    visibility = EnumField(Visibility, required=True)

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
