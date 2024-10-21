from draft_kings_client.client import DraftKingsOddsClient


client = DraftKingsOddsClient()
football_odds = client.get_football_markets()
alternate_spreads = client.get_football_alternate_spreads()
alternate_totals = client.get_football_alternate_totals()
client.continuous_harvest(client.get_football_markets)
