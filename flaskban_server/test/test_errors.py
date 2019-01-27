"""
The module contains unit tests for functions contained in 'error' module.
"""

# pylint: disable=no-self-use
# The reason for disabling self-use is that unittest package
# expects tests to be class methods.
# Without the self argument, the tests do not run.

import unittest.mock as mock
from unittest import TestCase

from errors import handle_error


class HandleErrorTest(TestCase):
    """
    Test case for handle_error decorator.
    """

    def test_calls_fun_when_no_error(self):
        """
        Tests if wrapper returns wrapped function's return value.
        """
        fun = mock.Mock(return_value='success')
        error_mock = mock.Mock()

        result = handle_error(error_mock)(fun)()

        self.assertEqual(result, 'success')

    def test_returns_defined_message_on_error_exception_no_message(self):
        """
        Tests if wrapper returns error response with message equal to argument message,
        when exception has no attribute named 'message'.
        """
        fun = mock.Mock(side_effect=ValueError)

        error_response, _ = handle_error(ValueError, message='caught')(fun)()

        self.assertEqual(error_response['message'], 'caught')

    def test_returns_defined_status_on_error_exception_no_message(self):
        """
        Tests if wrapper returns status passed in argument.
        """
        fun = mock.Mock(side_effect=ValueError)

        _, status = handle_error(ValueError, status=49)(fun)()

        self.assertEqual(status, 49)

    def test_returns_defined_message_on_error_exception_with_message(self):
        """
        Tests if wrapper returns error response with message equal to argument message,
        when exception has an attribute named 'message'.
        """
        error = ValueError('error')
        fun = mock.Mock(side_effect=error)

        error_response, _ = handle_error(ValueError, message='caught')(fun)()

        self.assertEqual(error_response['message'], 'caught')

    def test_returns_exception_message_when_no_message_parameter(self):
        """
        Tests if wrapper returns error response with message equal to exception's message attribute,
        when exception has an attribute named 'message'.
        """
        error = ValueError()
        error.message = 'error'
        fun = mock.Mock(side_effect=error)

        error_response, _ = handle_error(ValueError)(fun)()

        self.assertEqual(error_response['message'], 'error')
