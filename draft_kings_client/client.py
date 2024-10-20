import csv
import logging
from datetime import datetime, timezone

import requests
from draft_kings_client.authenticator import Authenticator
from draft_kings_client.models.odds_model import OddsModel

logging.basicConfig(level=logging.INFO)


class DraftKingsOddsClient:
    BASE_URL = 'https://sportsbook-nash.draftkings.com'
    SELECTIONS_URL = f'{BASE_URL}/api/sportscontent/dkusnj/v1/leagues/88808'
    SELECTION_INFO_URL = f'{BASE_URL}/api/sdinfo/dkusnj/v1/selectioninfo'

    def __init__(self, authenticator=None):
        self._authenticator = authenticator or Authenticator()
        self._session = requests.Session()

    @property
    def authenticator(self):
        return self._authenticator

    def _get_headers(self):
        """Retrieve the headers once and reuse them."""
        return self._authenticator.headers

    def _fetch_selection_ids(self):
        """Fetch selection IDs for football markets."""
        try:
            response = self._session.get(self.SELECTIONS_URL, headers=self._get_headers())
            response.raise_for_status()  # Raise an error for bad responses
            selections_json = response.json()
            return [selection['id'] for selection in selections_json.get('selections', [])]
        except requests.RequestException as e:
            logging.error(f"Failed to retrieve selections: {e}")
            return []

    def _fetch_odds_for_selection(self, selection_id):
        """Fetch odds for a given selection ID."""
        try:
            response = self._session.get(
                f"{self.SELECTION_INFO_URL}?siteName=dkusnj&selectionIds={selection_id}",
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logging.error(f"Failed to retrieve odds for selection {selection_id}: {e}")
            return None

    @staticmethod
    def _write_to_file(rows, filename='odds_dump.csv'):
        """Generic writer for rows."""
        if not rows:
            logging.info("No data to write to file.")
            return

        fieldnames = type(rows[0]).get_fieldnames()

        try:
            with open(filename, mode='w', newline='', encoding='utf-8-sig') as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                for row in rows:
                    writer.writerow(row.to_dict())
            logging.info(f"Data successfully written to {filename}")
        except IOError as e:
            logging.error(f"Failed to write data to file: {e}")

    def get_football_markets(self):
        """Main method to retrieve football markets and save them to a CSV."""
        football_odds_rows = []
        selection_ids = self._fetch_selection_ids()

        if not selection_ids:
            logging.info("No selection IDs retrieved.")
            return football_odds_rows

        for selection_id in selection_ids:
            odds_json = self._fetch_odds_for_selection(selection_id)

            if not odds_json or 'events' not in odds_json or 'markets' not in odds_json or 'selections' not in odds_json:
                logging.warning(f"Skipping selection {selection_id} due to incomplete data.")
                continue

            try:
                sportsbook = 'DraftKings'  # Consider making these top 3 strings enums when expanding
                sport = 'Football'
                league_info = 'NFL'
                game_date, game_time_with_zone = odds_json['events'][0]['startDate'].split('T')
                game_time = game_time_with_zone.split('.')[0]
                game_participants = odds_json['events'][0].get('betSlipLine', 'Unknown Participants')
                market = odds_json['markets'][0].get('betSlipLine', 'Unknown Market')
                bet_selection_name = odds_json['selections'][0].get('betSlipLine', 'Unknown Selection')
                price = odds_json['selections'][0]['displayOdds'].get('american', 'N/A')
                time_retrieved = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-1] + 'Z'
                suspended = odds_json['markets'][0].get('isSuspended', False)

                football_odds_rows.append(
                    OddsModel(sportsbook, sport, league_info, game_date, game_time, game_participants, market,
                              bet_selection_name, price, time_retrieved, suspended)
                )
            except KeyError as e:
                logging.error(f"Missing data for selection {selection_id}: {e}")
                continue

        self._write_to_file(football_odds_rows)
        return football_odds_rows
