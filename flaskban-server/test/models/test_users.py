import unittest.mock as mock

from common.errors import AlreadyExistsError, InvalidDataError
from models.users import User, UserRegisterSchema, UserLoginSchema
from unittest import TestCase
from marshmallow.exceptions import ValidationError


class UserTest(TestCase):
    def test_already_saved_calls_query(self):
        uut = User(name='john', password='pwd', email='john.smith@gmail.com')
        session_mock = mock.Mock()

        uut._already_saved(session_mock)
        session_mock.query.assert_called()

    def test_already_saved_returns_called_scalar(self):
        uut = User(name='john', password='pwd', email='john.smith@gmail.com')
        session_mock = mock.Mock()
        scalar_mock = mock.Mock()
        scalar_mock.scalar.return_value = True
        session_mock.query.return_value = scalar_mock

        result = uut._already_saved(session_mock)

        self.assertTrue(result)

    def test_save_calls_db(self):
        uut = User(name='john', password='pwd', email='john.smith@gmail.com')
        uut._already_saved = mock.Mock(return_value=False)

        with mock.patch('models.users.db') as mocked_db:
            uut.save()
            mocked_db.session.add.assert_called_with(uut)
            mocked_db.session.commit.assert_called()

    def test_raises_user_already_exists(self):
        with self.assertRaises(AlreadyExistsError):
            uut = User(name='present', password='pwd', email='already@exists.com')
            uut._already_saved = mock.Mock(return_value=True)

            uut.save()

    @mock.patch('models.users.pbkdf2_sha256')
    def test_init_hashes_password_kwarg(self, mocked_pbkdf2):
        User(name='dr. who', password='pwd', email='john.smith@gmail.com')
        mocked_pbkdf2.hash.assert_called_with('pwd')

    @mock.patch('models.users.pbkdf2_sha256')
    def test_init_does_not_hash_underscore_password_kwarg(self, mocked_pbkdf2):
        uut = User(name='dr. who', _password='pwd', email='john.smith@gmail.com')

        mocked_pbkdf2.hash.assert_not_called()
        self.assertEqual('pwd', uut.password)

    def test_save_raises_when_name_missing(self):
        with self.assertRaises(InvalidDataError):
            uut = User(password='pwd', email='john.smith@gmail.com')
            uut.save()

    def test_save_raises_when_password_missing(self):
        with self.assertRaises(InvalidDataError):
            uut = User(name='john', email='john.smith@gmail.com')
            uut.save()

    def test_save_raises_when_email_missing(self):
        with self.assertRaises(InvalidDataError):
            uut = User(name='john', password='pwd')
            uut.save()


class UserRegisterSchemaTest(TestCase):
    def test_load_raises_when_username_missing(self):
        with self.assertRaises(ValidationError):
            uut = UserRegisterSchema()
            uut.load({'email': 'test@ab.com', 'password': 'pwd'})

    def test_load_raises_when_email_missing(self):
        with self.assertRaises(ValidationError):
            uut = UserRegisterSchema()
            uut.load({'username': 'john', 'password': 'pwd'})

    def test_load_raises_when_password_missing(self):
        with self.assertRaises(ValidationError):
            uut = UserRegisterSchema()
            uut.load({'username': 'john', 'email': 'test@ab.com'})

    def test_loads_raises_when_invalid_email(self):
        with self.assertRaises(ValidationError):
            uut = UserRegisterSchema()
            uut.load({'username': 'john', 'password': 'pwd', 'email': 'testab.com'})

    def test_loads_raises_when_extra_data(self):
        with self.assertRaises(ValidationError):
            uut = UserRegisterSchema()
            uut.load({'username': 'john', 'password': 'pwd', 'email': 'test@ab.com', 'extra': 'data'})

    def test_loads_returns_correct_user_with_hashed_password(self):
        uut = UserRegisterSchema()

        result = uut.load({'username': 'john', 'password': 'pwd', 'email': 'test@ab.com'})

        self.assertEqual(result.name, 'john')
        self.assertEqual(result.email, 'test@ab.com')
        self.assertNotEqual(result.password, 'pwd')


class UserLoginSchemaTest(TestCase):
    def test_load_raises_when_username_and_email_missing(self):
        with self.assertRaises(ValidationError):
            uut = UserLoginSchema()
            uut.load({'password': 'pwd'})

    def test_load_raises_when_password_missing(self):
        with self.assertRaises(ValidationError):
            uut = UserLoginSchema()
            uut.load({'username': 'john', 'email': 'test@ab.com'})

    def test_loads_raises_when_invalid_email(self):
        with self.assertRaises(ValidationError):
            uut = UserLoginSchema()
            uut.load({'username': 'john', 'password': 'pwd', 'email': 'testab.com'})

    def test_loads_raises_when_extra_data(self):
        with self.assertRaises(ValidationError):
            uut = UserLoginSchema()
            uut.load({'username': 'john', 'password': 'pwd', 'email': 'test@ab.com', 'extra': 'data'})

    def test_loads_returns_correct_user_with_not_hashed_password(self):
        uut = UserLoginSchema()

        result = uut.load({'username': 'john', 'password': 'pwd', 'email': 'test@ab.com'})

        self.assertEqual(result.name, 'john')
        self.assertEqual(result.email, 'test@ab.com')
        self.assertEqual(result.password, 'pwd')

    def test_loads_returns_correct_user_when_only_username_given(self):
        uut = UserLoginSchema()

        result = uut.load({'username': 'john', 'password': 'pwd'})

        self.assertEqual(result.name, 'john')
        self.assertEqual(result.password, 'pwd')

    def test_loads_returns_correct_user_when_only_email_given(self):
        uut = UserLoginSchema()

        result = uut.load({'username': 'john', 'password': 'pwd', 'email': 'test@ab.com'})

        self.assertEqual(result.email, 'test@ab.com')
        self.assertEqual(result.password, 'pwd')
