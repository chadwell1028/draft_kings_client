import unittest
from unittest.mock import patch, MagicMock
from draft_kings_client.authenticator import Authenticator

class TestAuthenticator(unittest.TestCase):

    @patch('draft_kings_client.authenticator.requests.get')
    def test_generate_jwt_token_success(self, mock_get):
        # Mocking a successful response from the API
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{"token":"mocked_token"}'
        mock_get.return_value = mock_response

        authenticator = Authenticator()
        token = authenticator._generate_jwt_token()

        self.assertEqual(token, "mocked_token")
        self.assertEqual(authenticator.jwt_token, "mocked_token")

    @patch('draft_kings_client.authenticator.requests.get')
    def test_generate_jwt_token_failure(self, mock_get):
        # Mocking a failed response from the API
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        authenticator = Authenticator()
        token = authenticator._generate_jwt_token()

        self.assertIsNone(token)

if __name__ == '__main__':
    unittest.main()
