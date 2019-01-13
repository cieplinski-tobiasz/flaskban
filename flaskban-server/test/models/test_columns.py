"""
The module contains unit tests for functions and classes contained in 'columns' module.
"""

import unittest.mock as mock
from unittest import TestCase

from marshmallow import ValidationError

from models.columns import ColumnSchema


class ColumnSchemaTest(TestCase):
    """
    Test case for column schema. Covers validation of data.
    """

    def test_load_raises_when_name_missing(self):
        """
        Tests if load method raises ValidationError
        when name is not present.
        """
        uut = ColumnSchema()

        with self.assertRaises(ValidationError):
            uut.load({})

    def test_make_column_delegates_to_init(self):
        """
        Tests if make_column method delegates to
        model's __init__ method with given arguments.
        """
        ColumnSchema.__model__ = mock.Mock()
        data = {'test': 'data'}

        uut = ColumnSchema()
        uut.make_column(data)

        ColumnSchema.__model__.assert_called_once_with(**data)
