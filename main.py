import logging
from exchange import Exchange
from hitter import Hitter
from model import OrderRequest, Side
from trade import trade
from trade_config import TradeConfig
from ui import start_ui
from threading import Thread
USERNAME = "test2"
PASSWORD = "test2"


def main():
    trade_config = TradeConfig()
    cmi = Exchange(USERNAME, PASSWORD, sign_up_for_new_account=False)
    Thread(target=start_ui, args=(cmi,trade_config), daemon=True).start()
    while True:
        cmi.delete_all_orders()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
