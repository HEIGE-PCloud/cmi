import logging
from exchange import Exchange
from order import OrderRequest, Side

USERNAME = "Junrong"
PASSWORD = "ads100"


def main():
    cmi = Exchange(USERNAME, PASSWORD, sign_up_for_new_account=False)
    cmi.insert_order(order=OrderRequest(side=Side.BUY, price=0, volume=1, product="75 Call"))
    cmi.insert_order(order=OrderRequest(side=Side.BUY, price=0, volume=1, product="75 Call"))
    cmi.join()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
