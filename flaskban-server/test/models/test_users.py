import unittest.mock as mock
from unittest import TestCase

from marshmallow.exceptions import ValidationError

from errors import AlreadyExistsError, InvalidDataError, UnauthorizedError
from models.users import User, UserRegisterSchema, UserLoginSchema, login, register


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
            uut.load({'username': 'john', 'password': 'pwd',
                      'email': 'test@ab.com', 'extra': 'data'})

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
            uut.load({'username': 'john', 'password': 'pwd',
                      'email': 'test@ab.com', 'extra': 'data'})

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


class LoginTest(TestCase):
    def test_login_raises_when_no_user_with_name(self):
        User.find_by_name = mock.Mock(return_value=None)
        user = mock.Mock()
        user.name = 'test'

        with self.assertRaises(UnauthorizedError):
            login(user)

    def test_login_raises_when_no_user_with_email(self):
        User.find_by_email = mock.Mock(return_value=None)
        user = mock.Mock()
        user.name = None
        user.email = 'test@abc.com'

        with self.assertRaises(UnauthorizedError):
            login(user)

    @mock.patch('models.users.pbkdf2_sha256')
    def test_login_raises_when_bad_password(self, mocked_pbkdf2):
        user = mock.Mock()
        user.name = 'test'
        User.find_by_name = mock.Mock(return_value=user)
        mocked_pbkdf2.verify.return_value = False

        with self.assertRaises(UnauthorizedError):
            login(user)

    @mock.patch('models.users.create_access_token')
    @mock.patch('models.users.pbkdf2_sha256')
    def test_login_calls_create_access_token(self, mocked_pbkdf2, mocked_cat):
        user = mock.Mock()
        user.name = 'test'
        User.find_by_name = mock.Mock(return_value=user)
        mocked_pbkdf2.verify.return_value = True

        login(user)

        mocked_cat.assert_called()

    @mock.patch('models.users.create_access_token')
    @mock.patch('models.users.pbkdf2_sha256')
    def test_login_calls_verify(self, mocked_pbkdf2, _):
        user = mock.Mock()
        user.name = 'test'
        User.find_by_name = mock.Mock(return_value=user)
        mocked_pbkdf2.verify.return_value = True

        login(user)

        mocked_pbkdf2.verify.assert_called()

    @mock.patch('models.users.create_access_token', return_value='test_token')
    @mock.patch('models.users.pbkdf2_sha256')
    def test_login_returns_create_access_token(self, mocked_pbkdf2, _):
        user = mock.Mock()
        user.name = 'test'
        User.find_by_name = mock.Mock(return_value=user)
        mocked_pbkdf2.verify.return_value = True

        result = login(user)

        self.assertEqual(result, 'test_token')


class RegisterTest(TestCase):
    def test_register_delegates_to_save(self):
        user = mock.Mock()

        register(user)

        user.save.assert_called()
