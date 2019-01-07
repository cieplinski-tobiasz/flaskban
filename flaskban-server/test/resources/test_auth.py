import unittest.mock as mock

from http import HTTPStatus
from common.errors import AlreadyExistsError, InvalidDataError, UnauthorizedError
from resources.auth import Login, Register
from unittest import TestCase
from marshmallow.exceptions import ValidationError
from werkzeug.exceptions import BadRequest


class LoginTest(TestCase):

    @mock.patch('models.users.login_schema')
    @mock.patch('resources.auth.make_error_response')
    @mock.patch('resources.auth.request')
    def test_calls_error_response_when_validation_fails(self, request_mock, make_error_mock, login_schema_mock):
        request_mock.get_json.return_value = dict()
        login_schema_mock.load.raiseError.side_effect = ValidationError(message='test')
        uut = Login()

        uut.post()

        make_error_mock.assert_called_once_with(HTTPStatus.BAD_REQUEST, 'Invalid request body')

    @mock.patch('resources.auth.make_error_response')
    @mock.patch('resources.auth.request')
    def test_calls_error_response_when_bad_request_raised(self, request_mock, make_error_mock):
        request_mock.get_json.raiseError.side_effect = BadRequest()
        uut = Login()

        uut.post()

        make_error_mock.assert_called_once_with(HTTPStatus.BAD_REQUEST, 'Invalid request body')

    @mock.patch('resources.auth.login', side_effect=UnauthorizedError('test message'))
    @mock.patch('models.users.login_schema.load')
    @mock.patch('resources.auth.make_error_response')
    @mock.patch('resources.auth.request')
    def test_calls_error_response_when_login_fails(self, request_mock, make_error_mock, *_):
        request_mock.get_json.return_value = dict()
        uut = Login()

        uut.post()

        make_error_mock.assert_called_once_with(HTTPStatus.UNAUTHORIZED, 'test message')

    @mock.patch('resources.auth.login', return_value='test token')
    @mock.patch('models.users.login_schema.load')
    @mock.patch('resources.auth.request')
    def test_happy_path_returns_token(self, request_mock, *_):
        request_mock.get_json.return_value = dict()
        uut = Login()

        result_json, result_status = uut.post()

        self.assertEqual(result_json['token'], 'test token')
        self.assertEqual(result_status, HTTPStatus.OK)


class RegisterTest(TestCase):

    @mock.patch('resources.auth.make_error_response')
    @mock.patch('resources.auth.request')
    def test_calls_error_response_when_bad_request_raised(self, request_mock, make_error_mock):
        request_mock.get_json.raiseError.side_effect = BadRequest()
        uut = Register()

        uut.post()

        make_error_mock.assert_called_once_with(HTTPStatus.BAD_REQUEST, 'Invalid request body')

    @mock.patch('models.users.register_schema', side_effect=ValidationError(message='test'))
    @mock.patch('models.users.login_schema')
    @mock.patch('resources.auth.make_error_response')
    @mock.patch('resources.auth.request')
    def test_calls_error_response_when_register_validation_fails(self, request_mock, make_error_mock, *_):
        request_mock.get_json.return_value = dict()
        uut = Register()

        uut.post()

        make_error_mock.assert_called_once_with(HTTPStatus.BAD_REQUEST, 'Invalid request body')

    @mock.patch('models.users.register_schema')
    @mock.patch('models.users.login_schema', side_effect=ValidationError(message='test'))
    @mock.patch('resources.auth.make_error_response')
    @mock.patch('resources.auth.request')
    def test_calls_error_response_when_login_validation_fails(self, request_mock, make_error_mock, *_):
        request_mock.get_json.return_value = dict()
        uut = Register()

        uut.post()

        make_error_mock.assert_called_once_with(HTTPStatus.BAD_REQUEST, 'Invalid request body')

    @mock.patch('resources.auth.register', side_effect=AlreadyExistsError(message='test message'))
    @mock.patch('models.users.register_schema.load')
    @mock.patch('models.users.login_schema.load')
    @mock.patch('resources.auth.make_error_response')
    @mock.patch('resources.auth.request')
    def test_calls_error_response_when_user_already_exists(self, request_mock, make_error_mock, *_):
        request_mock.get_json.return_value = dict()
        uut = Register()

        uut.post()

        make_error_mock.assert_called_once_with(HTTPStatus.CONFLICT, 'test message')

    @mock.patch('resources.auth.register', side_effect=InvalidDataError(message='test message'))
    @mock.patch('models.users.register_schema.load')
    @mock.patch('models.users.login_schema.load')
    @mock.patch('resources.auth.make_error_response')
    @mock.patch('resources.auth.request')
    def test_calls_error_response_when_register_fails(self, request_mock, make_error_mock, *_):
        request_mock.get_json.return_value = dict()
        uut = Register()

        uut.post()

        make_error_mock.assert_called_once_with(HTTPStatus.BAD_REQUEST, 'Invalid request body')

    @mock.patch('resources.auth.login', side_effect=UnauthorizedError('test message'))
    @mock.patch('resources.auth.register')
    @mock.patch('models.users.register_schema.load')
    @mock.patch('models.users.login_schema.load')
    @mock.patch('resources.auth.request')
    def test_raises_when_login_fails(self, request_mock, *_):
        request_mock.get_json.return_value = dict()
        uut = Register()

        with self.assertRaises(UnauthorizedError):
            uut.post()

    @mock.patch('resources.auth.login', return_value='test token')
    @mock.patch('resources.auth.register')
    @mock.patch('models.users.register_schema.load')
    @mock.patch('models.users.login_schema.load')
    @mock.patch('resources.auth.make_error_response')
    @mock.patch('resources.auth.request')
    def test_happy_path_returns_token(self, request_mock, *_):
        request_mock.get_json.return_value = dict()
        uut = Login()

        result_json, result_status = uut.post()

        self.assertEqual(result_json['token'], 'test token')
        self.assertEqual(result_status, HTTPStatus.OK)
