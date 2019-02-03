"""
The module contains ORM domain for all domain specific objects.
"""

# pylint: disable=E1101
# Pylint has known issues when working with Flask-SQLAlchemy extension
# https://github.com/PyCQA/pylint/issues/1973

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

    def exists(self):
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

        if self.exists():
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
    columns = relationship('Column', cascade='delete', back_populates='board')

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

    def merge(self, other):
        """
        Updates `self` object with fields from another Board
        and stores the object in database.
        The only fields that are updated are `name` and `visibility`.
        Update occurs *only* if those fields are present in the `other` object,
        i. e. they are not equal to None.

        Args:
            other (Board): Object that will be used for update of self.
        """
        if other.name:
            self.name = other.name

        if other.visibility:
            self.visibility = other.visibility

        DB.session.merge(self)
        DB.session.commit()

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
    board_id = DB.Column(DB.Integer, DB.ForeignKey('board.id'), nullable=False)
    board = relationship('Board', back_populates='columns')
    tasks = relationship('Task', cascade='delete')

    __table_args__ = (
        DB.UniqueConstraint('board_id', 'name', name='_name_board_id_uc'),
        DB.UniqueConstraint('board_id', 'id', name='_col_id_board_id_uc')
    )

    @classmethod
    def exists_in_board_by_id(cls, board_id, column_id):
        """
        Checks if column with given id exists in a board with given id.

        Args:
            board_id (int): ID of the board.
            column_id (int): ID of the column.

        Returns:
            True if column exists, false otherwise.
        """
        return DB.session.query(
            cls.query.filter(
                (cls.board_id == board_id) & (cls.id_ == column_id)
            ).exists()).scalar()

    @classmethod
    def find_by_ids(cls, *, board_id, column_id):
        """
        Returns column belonging to board with `board_id`,
        if it exists within the board.

        Args:
            board_id (int): ID of the board.
            column_id (int): ID of the column.

        Returns:
            Column, if it exists within the board.

        Raises:
            NotFoundError: If board with given id does not exist,
                           or column with given id does not exist
                           within the board.
        """
        if not Board.exists_by_id(board_id):
            raise errors.NotFoundError(f'Board with id {board_id} does not exist')

        if not cls.exists_in_board_by_id(board_id, column_id):
            raise errors.NotFoundError(
                f'Column with id {column_id} does not exist in board with id {board_id}')

        return cls.query.filter((cls.board_id == board_id) & (cls.id_ == column_id)).one()

    @classmethod
    def delete(cls, *, board_id, column_id):
        """
        Deletes the column with given id belonging to board with given id from the database.

        All the tasks associated with the column are also deleted.

        Args:
            board_id (int): ID of the board.
            column_id (int): ID of the column.

        Raises:
            NotFoundError: If board with given id does not exist,
                           or column with given id does not exist
                           within the board.
        """
        column = cls.find_by_ids(board_id=board_id, column_id=column_id)
        DB.session.delete(column)
        DB.session.commit()

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

    def merge(self, other):
        """
        Updates `self` object with fields from another Column
        and stores the object in the database.
        The only field that is updated is `name`.
        Update occurs *only* if `name` is present in the `other` object,
        i. e. is not equal to None.

        Args:
            other (Column): Object that will be used for update of self.
        """
        if other.name:
            self.name = other.name

        DB.session.merge(self)
        DB.session.commit()

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


class Task(DB.Model):
    """
    Defines the ORM model for task.
    Task *always* belongs to exactly *one* column in the board.
    It may have user assigned, but it does not have to.

    Attributes:
        id_ (int): ID of the task.
        name (str): Name of the task.
        board_id (int): ID of the board that the task is in.
        column_id (int): ID of the column the task is assigned to.
        user_id (int): ID of the user assigned to the task.
    """
    id_ = DB.Column('id', DB.Integer, primary_key=True)
    name = DB.Column(DB.String(), nullable=False)
    description = DB.Column(DB.String())
    board_id = DB.Column(DB.Integer, DB.ForeignKey('board.id'), nullable=False)
    column_id = DB.Column(DB.Integer, DB.ForeignKey('column.id'), nullable=False)
    user_id = DB.Column(DB.Integer, DB.ForeignKey('user.id'), nullable=True)

    __table_args__ = (DB.UniqueConstraint('column_id', 'name', name='_name_col_id_uc'), )

    @classmethod
    def exists_in_column_by_name(cls, *, board_id, column_id, name):
        """
        Checks if task with given name exists in a column with given id.

        Args:
            board_id (int): ID of the board.
            column_id (int): ID of the column.
            name (str): Name of the task.

        Returns:
            True if task exists, false otherwise.

        Raises:
            NotFoundError: If board or column does not exist.
        """
        if not Board.exists_by_id(board_id):
            raise errors.NotFoundError(f'Board with id {board_id} does not exist')

        if not Column.exists_in_board_by_id(board_id, column_id):
            raise errors.NotFoundError(
                f'Column with id {column_id} does not exist in board with id {board_id}"')

        return DB.session.query(
            Task.query.filter(
                (Task.board_id == board_id) & (Task.column_id == column_id) & (Task.name == name)
            ).exists()).scalar()

    def save_to_board(self, board_id):
        """
        Stores the task in the database,
        associating it with given board id.

        Raises:
            NotFoundError: If board or column with given ID does not exist.
            AlreadyExistsError: If task with given name already exists
                                in a column with given ID.
        """

        self.board_id = board_id

        if Task.exists_in_column_by_name(board_id=board_id,
                                         column_id=self.column_id, name=self.name):
            raise errors.AlreadyExistsError(
                f'Task with name "{self.name}" already exists in column with id {self.column_id}')

        DB.session.add(self)
        DB.session.commit()
