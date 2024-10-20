# DraftKings Odds Client 🏈

![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.12%2B-blue)
![Version](https://img.shields.io/badge/version-0.1.0-blue)

## Overview 📖

The `DraftKingsOddsClient` is a Python client designed to fetch football odds from DraftKings Sportsbook. This project handles authentication, retrieves market data, and saves odds in a CSV file for easy analysis.

## Features ✨
- Fetch live NFL odds from DraftKings API
- Automatically refresh JWT tokens with a built-in authenticator
- Save odds to CSV for further data analysis
- Easy-to-use and customizable

## Installation 💻
1. Clone the repository:
   git clone https://github.com/chadwell1028/draft_kings_client.git
   cd draft_kings_gateway
2. Create a virtual environment
   python -m venv .venv 
   source .venv/bin/activate   # On Windows use: .\.venv\Scripts\activate
3. pip install -r requirements.txt

**Note:** If you want to install the client locally, run the below from the root directory:
```
pip install -e .
```

## Usage 🚀
```
from client import DraftKingsOddsClient


client = DraftKingsOddsClient()
football_odds = client.get_football_markets()
```

```
# Print the retrieved odds
for odds in football_odds:
    print(odds)
```


## Example Output 📊
```
[
  {
    'sportsbook': 'DraftKings',
    'sport': 'Football',
    'league_info': 'NFL',
    'game_date': '2024-10-20',
    'game_time': '18:00:00',
    'game_participants': 'Team A vs Team B',
    'market': 'Spread',
    'bet_selection_name': 'Team A -3.5',
    'price': '-110',
    'time_retrieved': '2024-10-20T17:30:00Z',
    'suspended': False
  },
  ...
]
```

## Testing 🔧
In the ../tests directory, run the following:

```pytest```