from typing import List
from cards import Cards
from exchange import Exchange

from strategy import Call, Future, Hedger, Pricer, Put, Strategy
from enum import Enum

class Mode(Enum):
    FULL_AUTO = 1
    MANUAL_NEWS = 2

class TradeConfig:

    def __init__(
        self,
        exchange: Exchange,
        cards: Cards,
        pricer: Pricer,
        future: Future,
        call: Call,
        put: Put,
        hedger: Hedger,
        mode: Mode
    ) -> None:
        self.exchange = exchange
        self.cards = cards
        self.pricer = pricer
        self.get_cards_value = None
        self.pricer.pricing()
        self.future = future
        self.call = call
        self.put = put
        self.hedger = hedger
        self.strategies: List[Strategy] = [future, call, put]
        self.mode = mode

    def update_cards(self, cards = None):
        self.pricer.reset()
        self.future.reset()
        self.call.reset()
        self.put.reset()
        self.hedger.reset()

        if cards is None:
            self.cards.set_chosen_cards(self.get_cards_value())
        else:
            self.cards.set_chosen_cards(cards)

        self.pricer.pricing()
