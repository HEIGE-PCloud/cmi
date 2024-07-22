import logging
from exchange import Exchange
from hitter import Hitter
from order import OrderRequest, Side

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
    cmi.insert_order(
        order=OrderRequest(side=Side.BUY, price=0, volume=1, product="75 C")
    )
    cmi.insert_order(
        order=OrderRequest(side=Side.BUY, price=0, volume=1, product="75 C")
    )
    cmi.join()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
