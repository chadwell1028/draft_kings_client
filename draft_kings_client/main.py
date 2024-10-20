from draft_kings_client.client import DraftKingsOddsClient


client = DraftKingsOddsClient()
football_odds = client.get_football_markets()
