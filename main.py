import logging
from threading import Thread

from cards import Cards
from exchange import Exchange
from strategy import Call, Future, Hedge, Pricer, Put
from trade import trade
from trade_config import TradeConfig
from ui import start_ui

logger = logging.getLogger(__name__)

USERNAME = "test"
PASSWORD = "test"

cmi = Exchange(USERNAME, PASSWORD, sign_up_for_new_account=False)


def main():
    cards = Cards()
    pricer = Pricer(cards, threads=4, iterations=100000)
    future = Future(cmi, "FUTURE", cards)
    call = Call(cmi, "150 CALL", cards, pricer)
    put = Put(cmi, "130 PUT", cards, pricer)
    hedge = Hedge(cmi, pricer)
    trade_config = TradeConfig(
        exchange=cmi,
        cards=cards,
        pricer=pricer,
        future=future,
        call=call,
        put=put,
        hedge=hedge,
    )
    Thread(target=start_ui, args=(cmi, trade_config), daemon=True).start()
    trade(trade_config)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        main()
    except Exception as error:
        cmi.delete_all_orders()
        print(error)
        logging.error(f"Exception thrown, cancelled all orders, quitting")
