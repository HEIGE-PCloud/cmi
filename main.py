import logging
from threading import Thread

from cards import Cards
from exchange import Exchange
from strategy import Call, Future, Pricer, Put
from trade import trade
from trade_config import TradeConfig
from ui import start_ui

USERNAME = "test2"
PASSWORD = "test2"


def main():
    cmi = Exchange(USERNAME, PASSWORD, sign_up_for_new_account=False)
    pricer = Pricer()
    cards = Cards()
    strategies = [
        Future(cmi, "FUTURE", cards),
        Call(cmi, "150 CALL", cards, pricer),
        Put(cmi, "130 PUT", cards, pricer),
    ]
    trade_config = TradeConfig(cmi, cards, pricer, strategies)
    Thread(target=start_ui, args=(cmi, trade_config), daemon=True).start()
    trade(trade_config)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
