import unittest.mock as mock

from common.errors import AlreadyExistsError, InvalidDataError
from models.users import User
from unittest import TestCase


class UserTest(TestCase):
    def test_already_saved_calls_query(self):
        uut = User(username='john', password='pwd', email='john.smith@gmail.com')
        session_mock = mock.Mock()

        uut._already_saved(session_mock)
        session_mock.query.assert_called()

    def test_already_saved_returns_called_scalar(self):
        uut = User(username='john', password='pwd', email='john.smith@gmail.com')
        session_mock = mock.Mock()
        scalar_mock = mock.Mock()
        scalar_mock.scalar.return_value = True
        session_mock.query.return_value = scalar_mock

        result = uut._already_saved(session_mock)

        self.assertTrue(result)

    def test_save_calls_db(self):
        uut = User(username='john', password='pwd', email='john.smith@gmail.com')
        uut._already_saved = mock.Mock(return_value=False)

        with mock.patch('models.users.db') as mocked_db:
            uut.save()
            mocked_db.session.add.assert_called_with(uut)
            mocked_db.session.commit.assert_called()

    def test_raises_user_already_exists(self):
        with self.assertRaises(AlreadyExistsError):
            uut = User(username='present', password='pwd', email='already@exists.com')
            uut._already_saved = mock.Mock(return_value=True)

            uut.save()

    @mock.patch('models.users.pbkdf2_sha256')
    def test_passwords_are_hashed(self, mocked_pbkdf2):
        User(username='dr. who', password='pwd', email='john.smith@gmail.com')
        mocked_pbkdf2.hash.assert_called_with('pwd')

    @mock.patch('models.users.pbkdf2_sha256')
    def test_password_getter_returns_hash(self, mocked_pbkdf2):
        mocked_pbkdf2.hash.return_value = 'hash'
        uut = User(username='dr. who', password='pwd', email='john.smith@gmail.com')

        hashed_pwd = uut.password

        self.assertEqual(hashed_pwd, 'hash')

    def test_save_raises_when_username_missing(self):
        with self.assertRaises(InvalidDataError):
            uut = User(password='pwd', email='john.smith@gmail.com')
            uut.save()

    def test_save_raises_when_password_missing(self):
        with self.assertRaises(InvalidDataError):
            uut = User(username='john', email='john.smith@gmail.com')
            uut.save()

    def test_save_raises_when_email_missing(self):
        with self.assertRaises(InvalidDataError):
            uut = User(username='john', password='pwd')
            uut.save()
