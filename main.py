import logging
from exchange import Exchange
from strategy import Future
from trade import trade
from trade_config import TradeConfig
from ui import start_ui
from threading import Thread
USERNAME = "test2"
PASSWORD = "test2"


def main():
    cmi = Exchange(USERNAME, PASSWORD, sign_up_for_new_account=False)
    trade_config = TradeConfig()
    future = Future(trade_config, cmi, 'FUTURE')
    trade_config.with_strategies([future])
    Thread(target=start_ui, args=(cmi,trade_config), daemon=True).start()
    trade(trade_config)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
