"""
The module contains unit tests for ORM models contained in `domain.models` module.
"""

from unittest import mock, TestCase

import domain.models
import errors


class BoardTest(TestCase):
    """
    Test case for board model.
    """

    @mock.patch('domain.models.DB')
    def test_save_calls_db(self, db_mock):
        """
        Tests if save method delegates to database object.
        """
        uut = domain.models.Board(name='test board', visibility='private')

        uut.save()

        db_mock.session.add.assert_called_with(uut)
        db_mock.session.commit.assert_called()

    def test_save_raises_name_not_present(self):
        """
        Tests if save method raises InvalidDataError
        when name of the board is not present.
        """
        uut = domain.models.Board(visibility='private')

        with self.assertRaises(errors.InvalidDataError):
            uut.save()

    def test_save_raises_visibility_not_present(self):
        """
        Tests if save method raises InvalidDataError
        when visibility of the board is not present.
        """
        uut = domain.models.Board(name='test name')

        with self.assertRaises(errors.InvalidDataError):
            uut.save()

    @mock.patch('domain.models.DB')
    def test_exists_by_id_calls_filter(self, db_mock):
        """
        Tests if exists_by_id method delegates to database object.
        """
        domain.models.Board.query = mock.Mock()

        domain.models.Board.exists_by_id(2)

        db_mock.session.query.assert_called_once()

    @mock.patch.object(domain.models.Board, 'exists_by_id', return_value=False)
    def test_delete_raises_when_no_board_with_id(self, _):
        """
        Tests if delete method raises NotFoundError
        when exists_by_id returns false.
        """
        with self.assertRaises(errors.NotFoundError):
            domain.models.Board.delete(5)

    @mock.patch.object(domain.models.Board, 'exists_by_id', return_value=True)
    @mock.patch('domain.models.DB')
    def test_delete_calls_filter_by_with_id(self, *_):
        """
        Tests if delete method
        to query class object's method.
        """
        domain.models.Board.query = mock.Mock()

        domain.models.Board.delete(5)

        domain.models.Board.query.filter_by.assert_called_once_with(id_=5)

    @mock.patch.object(domain.models.Board, 'exists_by_id', return_value=True)
    @mock.patch('domain.models.DB')
    def test_delete_calls_db(self, db_mock, _):
        """
        Tests if delete method
        to query class object's method.
        """
        domain.models.Board.query = mock.Mock()

        domain.models.Board.delete(5)

        db_mock.session.delete.assert_called_once()
        db_mock.session.commit.assert_called_once()

    def test_find_by_id_calls_get(self):
        """
        Tests if find_by_id method
        delegates to query class object's method.
        """
        domain.models.Board.query = mock.Mock()
        id_ = 5

        domain.models.Board.find_by_id(id_)

        domain.models.Board.query.get.assert_called_once_with(5)

    def test_find_by_id_raises_when_no_board_with_id(self):
        """
        Tests if find_by_id method
        delegates to query class object's method.
        """
        domain.models.Board.query = mock.Mock()
        domain.models.Board.query.get.return_value = None

        with self.assertRaises(errors.NotFoundError):
            domain.models.Board.find_by_id(5)


class UserTest(TestCase):
    """
    Test case for user model.
    """

    def test_save_calls_db(self):
        """
        Tests if save method delegates to database object.
        """
        uut = domain.models.User(name='john', password='pwd', email='john.smith@gmail.com')
        uut._already_saved = mock.Mock(return_value=False)

        with mock.patch('domain.models.DB') as mocked_db:
            uut.save()
            mocked_db.session.add.assert_called_with(uut)
            mocked_db.session.commit.assert_called()

    def test_raises_user_already_exists(self):
        """
        Tests if save raises AlreadyExistsError
        if user with given name or email already exists.
        """

        with self.assertRaises(errors.AlreadyExistsError):
            uut = domain.models.User(name='present', password='pwd', email='already@exists.com')
            uut._already_saved = mock.Mock(return_value=True)

            uut.save()

    @mock.patch('domain.models.pbkdf2_sha256')
    def test_init_hashes_password_kwarg(self, mocked_pbkdf2):
        """
        Tests if password is hashed if the __init__ method
        is called with `password` keyword argument.
        """
        domain.models.User(name='dr. who', password='pwd', email='john.smith@gmail.com')
        mocked_pbkdf2.hash.assert_called_with('pwd')

    @mock.patch('domain.models.pbkdf2_sha256')
    def test_init_does_not_hash_underscore_password_kwarg(self, mocked_pbkdf2):
        """
        Tests if password is *not* hashed if the __init__ method
        is called with `_password` keyword argument.
        """
        uut = domain.models.User(name='dr. who', _password='pwd', email='john.smith@gmail.com')

        mocked_pbkdf2.hash.assert_not_called()
        self.assertEqual('pwd', uut.password)

    def test_save_raises_when_name_missing(self):
        """
        Tests if save method raises InvalidDataError
        when username is missing.
        """
        with self.assertRaises(errors.InvalidDataError):
            uut = domain.models.User(password='pwd', email='john.smith@gmail.com')
            uut.save()

    def test_save_raises_when_password_missing(self):
        """
        Tests if save method raises InvalidDataError
        when password is missing.
        """
        with self.assertRaises(errors.InvalidDataError):
            uut = domain.models.User(name='john', email='john.smith@gmail.com')
            uut.save()

    def test_save_raises_when_email_missing(self):
        """
        Tests if save method raises InvalidDataError
        when email is missing.
        """
        with self.assertRaises(errors.InvalidDataError):
            uut = domain.models.User(name='john', password='pwd')
            uut.save()

    def test_login_raises_when_no_user_with_name(self):
        """
        Tests if login raises UnauthorizedError
        when no user with given name exists.
        """
        domain.models.User.find_by_name = mock.Mock(return_value=None)
        user = mock.Mock()
        user.name = 'test'

        with self.assertRaises(errors.UnauthorizedError):
            domain.models.User.login(user)

    def test_login_raises_when_no_user_with_email(self):
        """
        Tests if login raises UnauthorizedError
        when no user with given email exists.
        """
        domain.models.User.find_by_email = mock.Mock(return_value=None)
        user = mock.Mock()
        user.name = None
        user.email = 'test@abc.com'

        with self.assertRaises(errors.UnauthorizedError):
            domain.models.User.login(user)

    @mock.patch('domain.models.pbkdf2_sha256')
    def test_login_raises_when_bad_password(self, mocked_pbkdf2):
        """
        Tests if login raises UnauthorizedError
        when given password is invalid.
        """
        user = mock.Mock()
        user.name = 'test'
        domain.models.User.find_by_name = mock.Mock(return_value=user)
        mocked_pbkdf2.verify.return_value = False

        with self.assertRaises(errors.UnauthorizedError):
            domain.models.User.login(user)

    @mock.patch('domain.models.create_access_token')
    @mock.patch('domain.models.pbkdf2_sha256')
    def test_login_calls_create_access_token(self, mocked_pbkdf2, mocked_cat):
        """
        Tests if login delegates to create_access_token function.
        """
        user = mock.Mock()
        user.name = 'test'
        domain.models.User.find_by_name = mock.Mock(return_value=user)
        mocked_pbkdf2.verify.return_value = True

        domain.models.User.login(user)

        mocked_cat.assert_called()

    @mock.patch('domain.models.create_access_token')
    @mock.patch('domain.models.pbkdf2_sha256')
    def test_login_calls_verify(self, mocked_pbkdf2, _):
        """
        Tests if login delegates to verify function
        in order to compare the passwords.
        """
        user = mock.Mock()
        user.name = 'test'
        domain.models.User.find_by_name = mock.Mock(return_value=user)
        mocked_pbkdf2.verify.return_value = True

        domain.models.User.login(user)

        mocked_pbkdf2.verify.assert_called()

    @mock.patch('domain.models.create_access_token', return_value='test_token')
    @mock.patch('domain.models.pbkdf2_sha256')
    def test_login_returns_create_access_token(self, mocked_pbkdf2, _):
        """
        Tests if login returns the create_access_token function
        return value.
        """
        user = mock.Mock()
        user.name = 'test'
        domain.models.User.find_by_name = mock.Mock(return_value=user)
        mocked_pbkdf2.verify.return_value = True

        result = domain.models.User.login(user)

        self.assertEqual(result, 'test_token')

    def test_register_delegates_to_save(self):
        """
        Tests if register delegates to user's save method.
        """
        user = mock.Mock()

        domain.models.User.register(user)

        user.save.assert_called()


class ColumnTest(TestCase):
    """
    Test case for column model.
    """

    @mock.patch('domain.models.DB')
    def test_exists_in_board_by_id_calls_db(self, db_mock):
        """
        Tests if exists_in_board_by_id
        delegates to database object.
        """
        domain.models.Column.query = mock.Mock()
        uut = domain.models.Column()

        uut.exists_in_board_by_id(5)

        db_mock.session.query.assert_called_once()

    @mock.patch('domain.models.DB')
    def test_exists_in_board_by_name_calls_db(self, db_mock):
        """
        Tests if exists_in_board_by_name
        delegates to database object.
        """
        domain.models.Column.query = mock.Mock()
        uut = domain.models.Column()

        uut.exists_in_board_by_name(46)

        db_mock.session.query.assert_called_once()

    @mock.patch.object(domain.models.Board, 'exists_by_id', return_value=False)
    def test_save_to_board_raises_when_no_board_with_id(self, _):
        """
        Tests if save_to_board raises NotFoundError
        when board with given id does not exist.
        """
        uut = domain.models.Column()

        with self.assertRaises(errors.NotFoundError):
            uut.save_to_board(4)

    @mock.patch.object(domain.models.Board, 'exists_by_id', return_value=True)
    def test_save_to_board_raises_when_name_taken(self, _):
        """
        Tests if save_to_board raises NotFoundError
        when column with given name already exists
        within the board.
        """
        uut = domain.models.Column()
        uut.exists_in_board_by_name = mock.Mock(return_value=True)

        with self.assertRaises(errors.AlreadyExistsError):
            uut.save_to_board(4)

    @mock.patch.object(domain.models.Board, 'exists_by_id', return_value=True)
    @mock.patch('domain.models.DB')
    def test_save_to_board_calls_db(self, db_mock, _):
        """
        Tests if save_to_board
        delegates to database object.
        """
        uut = domain.models.Column()
        uut.exists_in_board_by_name = mock.Mock(return_value=False)

        uut.save_to_board(4)

        db_mock.session.add.assert_called_once_with(uut)
        db_mock.session.commit.assert_called_once()
