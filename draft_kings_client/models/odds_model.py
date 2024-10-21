class OddsModel:
    def __init__(self, sportsbook, sport, league_info, game_date, game_time, game_participants, market, bet_selection_name, price, time_retrieved, suspended, line):
        self._sportsbook = sportsbook
        self._sport = sport
        self._league_info = league_info
        self._game_date = game_date
        self._game_time = game_time
        self._game_participants = game_participants
        self._market = market
        self._bet_selection_name = bet_selection_name
        self._price = price
        self._time_retrieved = time_retrieved
        self._suspended = suspended
        self._line = line

    @property
    def sportsbook(self):
        return self._sportsbook

    @property
    def sport(self):
        return self._sport

    @property
    def league_info(self):
        return self._league_info

    @property
    def game_date(self):
        return self._game_date

    @property
    def game_time(self):
        return self._game_time

    @property
    def game_participants(self):
        return self._game_participants

    @property
    def market(self):
        return self._market

    @property
    def bet_selection_name(self):
        return self._bet_selection_name

    @property
    def price(self):
        return self._price

    @property
    def time_retrieved(self):
        return self._time_retrieved

    @property
    def suspended(self):
        return self._suspended

    @property
    def line(self):
        return self._line

    def to_dict(self):
        return {
            'sportsbook': self.sportsbook,
            'sport': self.sport,
            'league_info': self.league_info,
            'game_date': self.game_date,
            'game_time': self.game_time,
            'game_participants': self.game_participants,
            'market': self.market,
            'bet_selection_name': self.bet_selection_name,
            'price': self.price,
            'time_retrieved': self.time_retrieved,
            'suspended': self.suspended,
            'line': self.line
        }

    @staticmethod
    def get_fieldnames():
        return [
            'sportsbook', 'sport', 'league_info', 'game_date', 'game_time',
            'game_participants', 'market', 'bet_selection_name', 'price',
            'time_retrieved', 'suspended', 'line'
        ]
