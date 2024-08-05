from typing import List
from cards import Cards
from exchange import Exchange

from strategy import Pricer, Strategy


class TradeConfig:

    def __init__(
        self,
        exchange: Exchange,
        cards: Cards,
        pricer: Pricer,
        strategies: List[Strategy]
    ) -> None:
        self.exchange = exchange
        self.cards = cards
        self.pricer = pricer
        self.get_cards_value = None
        self.pricer.pricing()
        self.strategies = strategies

    def update_cards(self):
        self.pricer.reset()
        for strategy in self.strategies:
            strategy.reset_price()
        self.cards.set_chosen_cards(self.get_cards_value())
        self.pricer.pricing()
