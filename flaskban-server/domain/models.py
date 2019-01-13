"""
The module contains ORM domain for all domain specific objects.
"""
from enum import Enum

from flask_jwt_extended import create_access_token
from passlib.hash import pbkdf2_sha256
from sqlalchemy import exists
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

import errors
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

    def _already_saved(self):
        """
        Queries the database to check if user with given name or email has been stored.

        Returns:
            True if user already exists, False otherwise.
        """
        return User.query.filter(
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
            raise errors.InvalidDataError('Required fields are not present')

        if self._already_saved():
            raise errors.AlreadyExistsError('User already exists')

        DB.session.add(self)
        DB.session.commit()

    @staticmethod
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

    @staticmethod
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
            raise errors.UnauthorizedError('Wrong username or password')

        return create_access_token(identity=db_user.id_)

    def __repr__(self):
        return f'User(id={self.id_}, name={self.name}, email={self.email})'


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
    columns = relationship('Column', back_populates='board')

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
        return DB.session.query(cls.query.filter(cls.id_ == id_).exists()).scalar()

    @classmethod
    def find_by_id(cls, id_):
        """
        Queries the database for a board with given id.

        Args:
            id_ (int): ID of the board.

        Returns:
            Board with given ID.

        Raises:
            NotFoundError: If board with given ID does not exist.
        """
        board = cls.query.get(id_)

        if not board:
            raise errors.NotFoundError(f'Board with id {id_} does not exist')

        return board

    def save(self):
        """
        Stores the board in the database.

        Raises:
            InvalidDataError: If any of the fields in model is not present.
        """
        if not self.name or not self.visibility:
            raise errors.InvalidDataError('Required fields are not present')

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
            raise errors.NotFoundError(f'Board with id {id_} does not exist')

        board = cls.query.filter_by(id_=id_).one()
        DB.session.delete(board)
        DB.session.commit()

    def __repr__(self):
        return f'Board(id={self.id_}, name={self.name}, visibility={self.visibility.name})'


class Column(DB.Model):
    """
    Defines the ORM model for column in the kanban board.

    Attributes:
        id_ (int): ID of the column.
        name (str): Name of the column.
        board_id (int): ID of the board that the column is assigned to.
        board (Board): Board that the column is assigned to.
    """
    id_ = DB.Column('id', DB.Integer, primary_key=True)
    name = DB.Column(DB.String(), nullable=False)
    board_id = DB.Column(DB.Integer, DB.ForeignKey('board.id'))
    board = relationship('Board', cascade='all,delete', back_populates='columns')

    __table_args__ = (DB.UniqueConstraint('board_id', 'name', name='_name_board_id_uc'), )

    def exists_in_board_by_name(self, board_id):
        """
        Checks if column with given name exists in a board with given id.

        Args:
            board_id (int): ID of the board.

        Returns:
            True if column exists, false otherwise.
        """
        return DB.session.query(
            Column.query.filter(
                (Column.board_id == board_id) & (Column.name == self.name)
            ).exists()).scalar()

    def exists_in_board_by_id(self, board_id):
        """
        Checks if column with given id exists in a board with given id.

        Args:
            board_id (int): ID of the board.

        Returns:
            True if column exists, false otherwise.
        """
        return DB.session.query(
            Column.query.filter(
                (Column.board_id == board_id) & (Column.id_ == self.id_)
            ).exists()).scalar()

    def save_to_board(self, board_id):
        """
        Stores the column in the database,
        associating it with board with given id.

        Args:
            board_id (int): ID of the board.

        Raises:
            NotFoundError: If board with given ID does not exist.
            AlreadyExistsError: If column with given name already exists
                                in a board with given ID.
        """
        if not Board.exists_by_id(board_id):
            raise errors.NotFoundError(f'Board with id {board_id} does not exist')

        if self.exists_in_board_by_name(board_id):
            raise errors.AlreadyExistsError(
                f'Column with name "{self.name}" already exists in board with id {board_id}'
            )

        self.board_id = board_id
        DB.session.add(self)
        DB.session.commit()