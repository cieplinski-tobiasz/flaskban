"""
The module contains unit tests for schemas contained in `domain.schemas` module.
"""

from unittest import mock, TestCase

import marshmallow

import domain.schemas


class UserRegisterSchemaTest(TestCase):
    """
    Test case for UserRegisterSchema. Covers validation of data.
    """

    def test_load_raises_when_username_missing(self):
        """
        Tests if load method raises ValidationError
        when username is missing.
        """
        with self.assertRaises(marshmallow.ValidationError):
            uut = domain.schemas.UserRegisterSchema()
            uut.load({'email': 'test@ab.com', 'password': 'pwd'})

    def test_load_raises_when_email_missing(self):
        """
        Tests if load method raises ValidationError
        when email is missing.
        """
        with self.assertRaises(marshmallow.ValidationError):
            uut = domain.schemas.UserRegisterSchema()
            uut.load({'username': 'john', 'password': 'pwd'})

    def test_load_raises_when_password_missing(self):
        """
        Tests if load method raises ValidationError
        when password is missing.
        """
        with self.assertRaises(marshmallow.ValidationError):
            uut = domain.schemas.UserRegisterSchema()
            uut.load({'username': 'john', 'email': 'test@ab.com'})

    def test_loads_raises_when_invalid_email(self):
        """
        Tests if load method raises ValidationError
        when email is invalid.
        """
        with self.assertRaises(marshmallow.ValidationError):
            uut = domain.schemas.UserRegisterSchema()
            uut.load({'username': 'john', 'password': 'pwd', 'email': 'testab.com'})

    def test_loads_raises_when_extra_data(self):
        """
        Tests if load method raises ValidationError
        when data contains redundant fields.
        """
        with self.assertRaises(marshmallow.ValidationError):
            uut = domain.schemas.UserRegisterSchema()
            uut.load({'username': 'john', 'password': 'pwd',
                      'email': 'test@ab.com', 'extra': 'data'})

    def test_loads_returns_correct_user_with_hashed_password(self):
        """
        Tests if load method works properly
        when data is well formed (happy path).
        """
        uut = domain.schemas.UserRegisterSchema()

        result = uut.load({'username': 'john', 'password': 'pwd', 'email': 'test@ab.com'})

        self.assertEqual(result.name, 'john')
        self.assertEqual(result.email, 'test@ab.com')
        self.assertNotEqual(result.password, 'pwd')


class UserLoginSchemaTest(TestCase):
    """
    Test case for UserLoginSchema. Covers validation of data.
    """

    def test_load_raises_when_username_and_email_missing(self):
        """
        Tests if load method raises ValidationError
        when both username and email fields are missing.
        """
        with self.assertRaises(marshmallow.ValidationError):
            uut = domain.schemas.UserLoginSchema()
            uut.load({'password': 'pwd'})

    def test_load_raises_when_password_missing(self):
        """
        Tests if load method raises ValidationError
        when password is missing.
        """
        with self.assertRaises(marshmallow.ValidationError):
            uut = domain.schemas.UserLoginSchema()
            uut.load({'username': 'john', 'email': 'test@ab.com'})

    def test_loads_raises_when_invalid_email(self):
        """
        Tests if load method raises ValidationError
        when email is invalid.
        """
        with self.assertRaises(marshmallow.ValidationError):
            uut = domain.schemas.UserLoginSchema()
            uut.load({'username': 'john', 'password': 'pwd', 'email': 'testab.com'})

    def test_loads_raises_when_extra_data(self):
        """
        Tests if load method raises ValidationError
        when data contains redundant fields.
        """
        with self.assertRaises(marshmallow.ValidationError):
            uut = domain.schemas.UserLoginSchema()
            uut.load({'username': 'john', 'password': 'pwd',
                      'email': 'test@ab.com', 'extra': 'data'})

    def test_loads_returns_correct_user_with_not_hashed_password(self):
        """
        Tests if load method works properly when data is well formed
        and that it does *not* hash the password (happy path).
        """
        uut = domain.schemas.UserLoginSchema()

        result = uut.load({'username': 'john', 'password': 'pwd', 'email': 'test@ab.com'})

        self.assertEqual(result.name, 'john')
        self.assertEqual(result.email, 'test@ab.com')
        self.assertEqual(result.password, 'pwd')

    def test_loads_returns_correct_user_when_only_username_given(self):
        """
        Tests if load method works properly when only username and password are present
        and that it does *not* hash the password (happy path).
        """
        uut = domain.schemas.UserLoginSchema()

        result = uut.load({'username': 'john', 'password': 'pwd'})

        self.assertEqual(result.name, 'john')
        self.assertEqual(result.password, 'pwd')

    def test_loads_returns_correct_user_when_only_email_given(self):
        """
        Tests if load method works properly when only email and password are present
        and that it does *not* hash the password (happy path).
        """
        uut = domain.schemas.UserLoginSchema()

        result = uut.load({'username': 'john', 'password': 'pwd', 'email': 'test@ab.com'})

        self.assertEqual(result.email, 'test@ab.com')
        self.assertEqual(result.password, 'pwd')


class BoardSchemaTest(TestCase):
    """
    Test case for board schema. Covers validation of data.
    """

    def test_load_raises_when_name_missing(self):
        """
        Tests if load method raises ValidationError
        when name is not present.
        """
        uut = domain.schemas.BoardSchema()

        with self.assertRaises(marshmallow.ValidationError):
            uut.load({'visibility': 'private'})

    def test_load_raises_when_visibility_missing(self):
        """
        Tests if load method raises ValidationError
        when visibility is not present.
        """
        uut = domain.schemas.BoardSchema()

        with self.assertRaises(marshmallow.ValidationError):
            uut.load({'name': 'test'})

    def test_load_raises_when_visibility_invalid(self):
        """
        Tests if load method raises ValidationError
        when visibility is not a valid enum.
        """

        uut = domain.schemas.BoardSchema()

        with self.assertRaises(marshmallow.ValidationError):
            uut.load({'name': 'test', 'visibility': 'no-such-visibility'})

    def test_make_board_delegates_to_init(self):
        """
        Tests if make_board method delegates to
        model's __init__ method with given arguments.
        """
        domain.schemas.BoardSchema.__model__ = mock.Mock()
        data = {'test': 'data'}

        uut = domain.schemas.BoardSchema()
        uut.make_board(data)

        domain.schemas.BoardSchema.__model__.assert_called_once_with(**data)


class ColumnSchemaTest(TestCase):
    """
    Test case for column schema. Covers validation of data.
    """

    def test_load_raises_when_name_missing(self):
        """
        Tests if load method raises ValidationError
        when name is not present.
        """
        uut = domain.schemas.ColumnSchema()

        with self.assertRaises(marshmallow.ValidationError):
            uut.load({})

    @mock.patch.object(domain.schemas.ColumnSchema, '__model__')
    def test_make_column_delegates_to_init(self, model_mock):
        """
        Tests if make_column method delegates to
        model's __init__ method with given arguments.
        """
        data = {'test': 'data'}

        uut = domain.schemas.ColumnSchema()
        uut.make_column(data)

        model_mock.assert_called_once_with(**data)
