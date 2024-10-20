import unittest
from unittest.mock import patch, MagicMock
from draft_kings_client.client import DraftKingsOddsClient
from draft_kings_client.models.odds_model import OddsModel


class TestDraftKingsOddsClient(unittest.TestCase):

    @patch('draft_kings_client.client.requests.Session.get')
    def test_fetch_selection_ids(self, mock_get):
        # Mock the response from SELECTIONS_URL
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'selections': [{'id': '12345'}, {'id': '67890'}]
        }

        mock_get.return_value = mock_response

        client = DraftKingsOddsClient()
        selection_ids = client._fetch_selection_ids()

        self.assertEqual(selection_ids, ['12345', '67890'])
        mock_get.assert_called_once_with(
            client.SELECTIONS_URL,
            headers=client._get_headers()
        )

    @patch('draft_kings_client.client.requests.Session.get')
    def test_fetch_odds_for_selection(self, mock_get):
        # Mock the odds response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'events': [{
                'startDate': '2024-10-20T18:00:00.000Z',
                'betSlipLine': 'Team A vs Team B'
            }],
            'markets': [{
                'betSlipLine': 'Spread',
                'isSuspended': False
            }],
            'selections': [{
                'betSlipLine': 'Team A -3.5',
                'displayOdds': {'american': '-110'}
            }]
        }
        mock_get.return_value = mock_response

        client = DraftKingsOddsClient()
        selection_id = '12345'
        odds_data = client._fetch_odds_for_selection(selection_id)

        expected_url = f"{client.SELECTION_INFO_URL}?siteName=dkusnj&selectionIds={selection_id}"
        mock_get.assert_called_once_with(
            expected_url,
            headers=client._get_headers()
        )

        self.assertIn('events', odds_data)
        self.assertIn('markets', odds_data)
        self.assertIn('selections', odds_data)

    @patch.object(DraftKingsOddsClient, '_write_to_file')
    @patch.object(DraftKingsOddsClient, '_fetch_odds_for_selection')
    @patch.object(DraftKingsOddsClient, '_fetch_selection_ids')
    def test_get_football_markets(self, mock_fetch_selection_ids, mock_fetch_odds_for_selection, mock_write_to_file):
        # Mock the selection IDs
        mock_fetch_selection_ids.return_value = ['12345', '67890']

        # Mock the odds data for each selection ID
        odds_response = {
            'events': [{
                'startDate': '2024-10-20T18:00:00.000Z',
                'betSlipLine': 'Team A vs Team B'
            }],
            'markets': [{
                'betSlipLine': 'Spread',
                'isSuspended': False
            }],
            'selections': [{
                'betSlipLine': 'Team A -3.5',
                'displayOdds': {'american': '-110'}
            }]
        }
        mock_fetch_odds_for_selection.return_value = odds_response

        client = DraftKingsOddsClient()

        football_odds_rows = client.get_football_markets()

        self.assertEqual(len(football_odds_rows), 2)  # We have two selection IDs
        for odds in football_odds_rows:
            self.assertIsInstance(odds, OddsModel)
            self.assertEqual(odds.sportsbook, 'DraftKings')
            self.assertEqual(odds.sport, 'Football')
            self.assertEqual(odds.league_info, 'NFL')
            self.assertEqual(odds.game_date, '2024-10-20')
            self.assertEqual(odds.game_time, '18:00:00')
            self.assertEqual(odds.game_participants, 'Team A vs Team B')
            self.assertEqual(odds.market, 'Spread')
            self.assertEqual(odds.bet_selection_name, 'Team A -3.5')
            self.assertEqual(odds.price, '-110')
            self.assertFalse(odds.suspended)
            self.assertIsInstance(odds.time_retrieved, str)
            self.assertTrue(len(odds.time_retrieved) > 0)

        mock_fetch_selection_ids.assert_called_once()
        self.assertEqual(mock_fetch_odds_for_selection.call_count, 2)
        mock_fetch_odds_for_selection.assert_any_call('12345')
        mock_fetch_odds_for_selection.assert_any_call('67890')
        mock_write_to_file.assert_called_once_with(football_odds_rows)

if __name__ == '__main__':
    unittest.main()
