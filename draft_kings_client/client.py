import csv
import logging
import os
from datetime import datetime, timezone
from time import sleep

import requests
from draft_kings_client.authenticator import Authenticator
from draft_kings_client.models.odds_model import OddsModel

logging.basicConfig(level=logging.INFO)


class DraftKingsOddsClient:
    BASE_URL = 'https://sportsbook-nash.draftkings.com'
    SELECTIONS_URL = f'{BASE_URL}/api/sportscontent/dkusnj/v1/leagues/88808'
    SELECTION_INFO_URL = f'{BASE_URL}/api/sdinfo/dkusnj/v1/selectioninfo'
    ALTERNATE_SPREAD_SELECTION_URL = f'{BASE_URL}/api/sportscontent/dkusnj/v1/leagues/88808/categories/492/subcategories/13195'
    ALTERNATE_TOTAL_SELECTION_URL = f'{BASE_URL}/api/sportscontent/dkusnj/v1/leagues/88808/categories/492/subcategories/13196'

    def __init__(self, authenticator=None):
        self._authenticator = authenticator or Authenticator()
        self._session = requests.Session()

    @property
    def authenticator(self):
        return self._authenticator

    def _get_headers(self):
        '''Retrieve the headers once and reuse them.'''
        return self._authenticator.headers

    def _fetch_selection_ids(self, selections_url=None):
        '''Fetch selection IDs for football markets.'''
        try:
            if not selections_url:
                selections_url = self.SELECTIONS_URL

            response = self._session.get(selections_url, headers=self._get_headers())
            response.raise_for_status()  # Raise an error for bad responses
            selections_json = response.json()
            return [selection['id'] for selection in selections_json.get('selections', [])]
        except requests.RequestException as e:
            logging.error(f'Failed to retrieve selections: {e}')
            return []

    def _fetch_odds_for_selection(self, selection_id):
        '''Fetch odds for a given selection ID.'''
        try:
            response = self._session.get(
                f'{self.SELECTION_INFO_URL}?siteName=dkusnj&selectionIds={selection_id}',
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logging.error(f'Failed to retrieve odds for selection {selection_id}: {e}')
            return None

    @staticmethod
    def _write_to_file(rows, filename='odds_dump.csv', append=False):
        '''Generic writer for rows, appending to the file if append is True.'''
        if not rows:
            logging.info('No data to write to file.')
            return

        fieldnames = type(rows[0]).get_fieldnames()

        try:
            mode = 'a' if append else 'w'
            file_exists = os.path.isfile(filename)

            with open(filename, mode=mode, newline='', encoding='utf-8-sig') as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)

                if not append or (append and (not file_exists or os.path.getsize(filename) == 0)):
                    writer.writeheader()
                for row in rows:
                    writer.writerow(row.to_dict())
            if append:
                logging.info(f'Data successfully appended to {filename}')
            else:
                logging.info(f'Data successfully written to {filename}')
        except IOError as e:
            logging.error(f'Failed to write data to file: {e}')

    @staticmethod
    def continuous_harvest(func, seconds=10):
        while True:
            logging.info(f'Running continuous harvest for method: {func}')
            func(append=True)

            logging.info(f'Sleeping for {seconds} seconds.')
            sleep(seconds)

    def get_football_markets(self, append=False):
        '''Main method to retrieve football markets and save them to a CSV.'''
        football_odds_rows = []
        selection_ids = self._fetch_selection_ids()

        if not selection_ids:
            logging.info('No selection IDs retrieved.')
            return football_odds_rows

        for selection_id in selection_ids:
            odds_json = self._fetch_odds_for_selection(selection_id)

            if not odds_json or 'events' not in odds_json or 'markets' not in odds_json or 'selections' not in odds_json:
                logging.warning(f'Skipping selection {selection_id} due to incomplete data.')
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
                line = 'MAIN'

                football_odds_rows.append(
                    OddsModel(sportsbook, sport, league_info, game_date, game_time, game_participants, market,
                              bet_selection_name, price, time_retrieved, suspended, line)
                )
            except KeyError as e:
                logging.error(f'Missing data for selection {selection_id}: {e}')
                continue

        self._write_to_file(football_odds_rows, append=append)
        return football_odds_rows

    def get_football_alternate_spreads(self, append=False):
        '''Method to retrieve football alternate spreads and save them to a CSV.'''
        alternate_spread_rows = []
        selection_ids = self._fetch_selection_ids(self.ALTERNATE_SPREAD_SELECTION_URL)

        if not selection_ids:
            logging.info('No selection IDs retrieved.')
            return alternate_spread_rows

        for selection_id in selection_ids:
            odds_json = self._fetch_odds_for_selection(selection_id)

            if not odds_json or 'events' not in odds_json or 'markets' not in odds_json or 'selections' not in odds_json:
                logging.warning(f'Skipping selection {selection_id} due to incomplete data.')
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
                line = 'ALTERNATE'

                alternate_spread_rows.append(
                    OddsModel(sportsbook, sport, league_info, game_date, game_time, game_participants, market,
                              bet_selection_name, price, time_retrieved, suspended, line)
                )
            except KeyError as e:
                logging.error(f'Missing data for selection {selection_id}: {e}')
                continue

        self._write_to_file(alternate_spread_rows, filename='odds_alternate_spreads_dump.csv', append=append)
        return alternate_spread_rows

    def get_football_alternate_totals(self, append=False):
        '''Method to retrieve football alternate totals and save them to a CSV.'''
        alternate_totals_rows = []
        selection_ids = self._fetch_selection_ids(self.ALTERNATE_TOTAL_SELECTION_URL)

        if not selection_ids:
            logging.info('No selection IDs retrieved.')
            return alternate_totals_rows

        for selection_id in selection_ids:
            odds_json = self._fetch_odds_for_selection(selection_id)

            if not odds_json or 'events' not in odds_json or 'markets' not in odds_json or 'selections' not in odds_json:
                logging.warning(f'Skipping selection {selection_id} due to incomplete data.')
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
                line = 'ALTERNATE'

                alternate_totals_rows.append(
                    OddsModel(sportsbook, sport, league_info, game_date, game_time, game_participants, market,
                              bet_selection_name, price, time_retrieved, suspended, line)
                )
            except KeyError as e:
                logging.error(f'Missing data for selection {selection_id}: {e}')
                continue

        self._write_to_file(alternate_totals_rows, filename='odds_alternate_totals_dump.csv', append=append)
        return alternate_totals_rows
