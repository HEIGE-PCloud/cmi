import logging
from exchange import Exchange
from hitter import Hitter
from model import OrderRequest, Side

USERNAME = "Junrong"
PASSWORD = "ads100"


def main():
    hitters = [
        Hitter("75 C", low_price=0, high_price=1000),
        Hitter("Sum", low_price=0, high_price=1000),
        Hitter("65 P", low_price=0, high_price=1000),
        Hitter("70 Straddle", low_price=0, high_price=1000),
    ]
    cmi = Exchange(USERNAME, PASSWORD, hitters, sign_up_for_new_account=False)
    cmi.trade()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
