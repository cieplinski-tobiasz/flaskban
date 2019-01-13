"""
The module contains the Column model and validation schema.
"""
from extensions import DB

from marshmallow import Schema, fields, post_load
from sqlalchemy.orm import relationship


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
    board = relationship('Board', back_populates='columns')


class ColumnSchema(Schema):
    """
    Defines a validation and serialization schema for column.
    """
    __model__ = Column

    id_ = fields.Integer(data_key='id', dump_only=True)
    name = fields.Str(required=True)

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
