from typing import List
from cards import Cards
from exchange import Exchange

from strategy import Call, Future, Hedge, Pricer, Put


class TradeConfig:

    def __init__(
        self,
        exchange: Exchange,
        cards: Cards,
        pricer: Pricer,
        future: Future,
        call: Call,
        put: Put,
        hedge: Hedge
    ) -> None:
        self.exchange = exchange
        self.cards = cards
        self.pricer = pricer
        self.get_cards_value = None
        self.pricer.pricing()
        self.future = future
        self.call = call
        self.put = put
        self.hedge = hedge

    def update_cards(self, cards = None):
        self.pricer.reset()
        self.future.reset()
        self.call.reset()
        self.put.reset()
        self.hedge.reset()

        if cards is None:
            self.cards.set_chosen_cards(self.get_cards_value())
        else:
            self.cards.set_chosen_cards(cards)

        self.pricer.pricing()
