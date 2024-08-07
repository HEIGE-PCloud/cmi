import logging
from threading import Thread

from cards import Cards
from exchange import Exchange
from strategy import Call, Future, Hedger, Pricer, Put
from trade import trade
from trade_config import TradeConfig
from ui import start_ui

logger = logging.getLogger(__name__)

USERNAME = "test"
PASSWORD = "test"
DEFAULT_FUTURE_SYMBOL = "FUTURE"
DEFAULT_CALL_SYMBOL = "150 CALL"
DEFAULT_PUT_SYMBOL = "130 PUT"
DEFAULT_STRATEGY_INTERVAL = 9
DEFAULT_HEDGER_INTERVAL = 9.1
DEFAULT_THREAD_COUNT = 10
DEFAULT_ITERATION_COUNT = 100000

cmi = Exchange(USERNAME, PASSWORD, sign_up_for_new_account=False)


def main():
    cards = Cards()
    pricer = Pricer(cards, threads=DEFAULT_THREAD_COUNT, iterations=DEFAULT_ITERATION_COUNT)
    future = Future(cmi, DEFAULT_FUTURE_SYMBOL, cards, DEFAULT_STRATEGY_INTERVAL)
    call = Call(cmi, DEFAULT_CALL_SYMBOL, cards, pricer, DEFAULT_STRATEGY_INTERVAL)
    put = Put(cmi, DEFAULT_PUT_SYMBOL, cards, pricer, DEFAULT_STRATEGY_INTERVAL)
    hedger = Hedger(exchange=cmi, pricer=pricer, future=future, call=call, put=put, interval=DEFAULT_HEDGER_INTERVAL)
    trade_config = TradeConfig(
        exchange=cmi,
        cards=cards,
        pricer=pricer,
        future=future,
        call=call,
        put=put,
        hedger=hedger,
    )
    Thread(target=start_ui, args=(cmi, trade_config), daemon=True).start()
    trade(trade_config)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        main()
    except Exception as error:
        cmi.delete_all_orders()
        logger.exception(error)
        logger.error(f"Exception thrown, cancelled all orders, quitting")
