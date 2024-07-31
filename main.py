import logging
from exchange import Exchange
from hitter import Hitter
from model import OrderRequest, Side
from trade_config import TradeConfig
from ui import start_ui
from threading import Thread
USERNAME = "test1"
PASSWORD = "test1"


def main():
    cmi = Exchange(USERNAME, PASSWORD, sign_up_for_new_account=False)
    trade_config = TradeConfig()
    Thread(target=start_ui, args=(cmi,trade_config), daemon=True).start()
    cmi.trade()
    cmi.insert_order(OrderRequest(side=Side.BUY, price=1, volume=10, product="FUTURE"))
    cmi.delete_all_orders()
    cmi.join()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
