"""
The module contains unit tests for functions and classes contained in 'boards' module.
"""

import unittest.mock as mock
from unittest import TestCase

from marshmallow import ValidationError

from errors import InvalidDataError
from models.boards import Board, BoardSchema


class BoardTest(TestCase):
    """
    Test case for board model.
    """

    def test_save_calls_db(self):
        """
        Tests if save method delegates to database object.
        """
        uut = Board(name='test board', visibility='private')

        with mock.patch('models.boards.DB') as mocked_db:
            uut.save()
            mocked_db.session.add.assert_called_with(uut)
            mocked_db.session.commit.assert_called()

    def test_save_raises_name_not_present(self):
        """
        Tests if save method raises InvalidDataError
        when name of the board is not present.
        """
        uut = Board(visibility='private')

        with self.assertRaises(InvalidDataError):
            uut.save()

    def test_save_raises_visibility_not_present(self):
        """
        Tests if save method raises InvalidDataError
        when visibility of the board is not present.
        """
        uut = Board(name='test name')

        with self.assertRaises(InvalidDataError):
            uut.save()

    def test_find_by_name_calls_filter_by(self):
        """
        Tests if find_by_name method
        delegates to query class object.
        """
        Board.query = mock.Mock()

        Board.find_by_name(name='test')

        Board.query.filter_by.assert_called_once_with(name='test')

    def test_exists_by_id_calls_filter_by(self):
        """
        Tests if exists_by_id method
        delegates to query class object.
        """

        Board.query = mock.Mock()

        Board.exists_by_id(id_=2)

        Board.query.filter_by.assert_called_once()


class BoardSchemaTest(TestCase):
    """
    Test case for board schema. Covers validation of data.
    """

    def test_load_raises_when_name_missing(self):
        """
        Tests if load method raises ValidationError
        when name is not present.
        """
        uut = BoardSchema()

        with self.assertRaises(ValidationError):
            uut.load({'visibility': 'private'})

    def test_load_raises_when_visibility_missing(self):
        """
        Tests if load method raises ValidationError
        when visibility is not present.
        """
        uut = BoardSchema()

        with self.assertRaises(ValidationError):
            uut.load({'name': 'test'})

    def test_load_raises_when_visibility_invalid(self):
        """
        Tests if load method raises ValidationError
        when visibility is not a valid enum.
        """

        uut = BoardSchema()

        with self.assertRaises(ValidationError):
            uut.load({'name': 'test', 'visibility': 'no-such-visibility'})

    def test_make_board_delegates_to_init(self):
        """
        Tests if make_board method delegates to
        model's __init__ method with given arguments.
        """
        BoardSchema.__model__ = mock.Mock()
        data = {'test': 'data'}

        uut = BoardSchema()
        uut.make_board(data)

        BoardSchema.__model__.assert_called_once_with(**data)
