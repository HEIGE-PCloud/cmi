import logging
from exchange import Exchange
from hitter import Hitter
from model import OrderRequest, Side
from ui import start_ui
from threading import Thread
USERNAME = "Junrong"
PASSWORD = "ads100"


def main():
    cmi = Exchange(USERNAME, PASSWORD, sign_up_for_new_account=False)
    Thread(target=start_ui, args=(cmi,), daemon=True).start()
    cmi.trade()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
