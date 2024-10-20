import requests
import re
import logging
import time
from requests.exceptions import RequestException, Timeout

logging.basicConfig(level=logging.INFO)


class Authenticator:
    def __init__(self, auth_endpoint='https://gaming-us-nj.draftkings.com/api/wager/v1/generateAnonymousEnterpriseJWT',
                 headers=None):
        self._auth_endpoint = auth_endpoint
        self._headers = headers
        self._jwt_token = None

    @property
    def auth_endpoint(self):
        return self._auth_endpoint

    @property
    def headers(self):
        if not self._headers:
            self._generate_headers()
        return self._headers

    @property
    def jwt_token(self):
        if not self._jwt_token:
            self._generate_jwt_token()
        return self._jwt_token

    def _generate_jwt_token(self):
        jwt_token = None
        retries = 3
        retry_delay = 2

        for attempt in range(retries):
            try:
                logging.info(f"Attempt {attempt + 1}: Requesting JWT token from {self._auth_endpoint}")
                response = requests.get(self._auth_endpoint, timeout=10)

                if response.status_code == 200:
                    token_match = re.search(r'"token":"(.*?)"', response.text)

                    if token_match:
                        jwt_token = token_match.group(1)
                        self._jwt_token = jwt_token
                        logging.info(f"JWT Token successfully retrieved: {jwt_token}")
                        return jwt_token
                    else:
                        logging.error("Token not found in response")
                else:
                    logging.error(f"Failed to retrieve token, status code: {response.status_code}")
                    logging.error(f"Response content: {response.text}")

            except Timeout:
                logging.error("The request timed out while trying to reach the authentication endpoint.")

            except RequestException as e:
                logging.error(f"An error occurred while making the request: {e}")

            except Exception as e:
                logging.error(f"An unexpected error occurred: {e}")

            if attempt < retries - 1:
                logging.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay *= 2  # double delay after each retry

        logging.error(f"Failed to retrieve JWT token after {retries} attempts.")
        return jwt_token

    def _generate_headers(self):
        if not self.jwt_token:
            logging.error("Cannot generate headers without a valid JWT token.")
            return None

        headers = {
            'Authorization': f'Bearer {self.jwt_token}',
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'Cache-Control': 'no-cache',
            'Origin': 'https://sportsbook.draftkings.com',
            'Pragma': 'no-cache',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36'
        }

        self._headers = headers
        logging.info("Headers successfully generated.")

        return headers
