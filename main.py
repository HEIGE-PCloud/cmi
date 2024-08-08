import logging
from threading import Thread

from cards import Cards
from exchange import Exchange
from strategy import Call, Future, Hedger, Pricer, Put
from trade import full_auto_trade, manual_news_trade
from trade_config import Mode, TradeConfig
from ui import start_ui
import argparse

logger = logging.getLogger(__name__)

USERNAME = "test"
PASSWORD = "test"
DEFAULT_FUTURE_SYMBOL = "FUTURE"
DEFAULT_CALL_SYMBOL = "150 CALL"
DEFAULT_PUT_SYMBOL = "130 PUT"
DEFAULT_STRATEGY_INTERVAL = 9
DEFAULT_HEDGER_INTERVAL = 9.1
DEFAULT_THREAD_COUNT = 10
DEFAULT_ITERATION_COUNT = 200000
DEFAULT_MODE = Mode.FULL_AUTO

cmi = Exchange(USERNAME, PASSWORD, sign_up_for_new_account=False)


def parse_args():
    parser = argparse.ArgumentParser(description='cmi')
    parser.add_argument('--manual', action='store_true', help='Set the manual mode')
    args = parser.parse_args()
    if args.manual:
        global DEFAULT_MODE
        DEFAULT_MODE = Mode.MANUAL_NEWS


def main():
    parse_args()

    cards = Cards()
    pricer = Pricer(
        cards,
        thread_count=DEFAULT_THREAD_COUNT,
        iteration_count=DEFAULT_ITERATION_COUNT,
    )
    future = Future(cmi, DEFAULT_FUTURE_SYMBOL, cards, DEFAULT_STRATEGY_INTERVAL)
    call = Call(cmi, DEFAULT_CALL_SYMBOL, cards, pricer, DEFAULT_STRATEGY_INTERVAL)
    put = Put(cmi, DEFAULT_PUT_SYMBOL, cards, pricer, DEFAULT_STRATEGY_INTERVAL)
    hedger = Hedger(
        exchange=cmi,
        pricer=pricer,
        future=future,
        call=call,
        put=put,
        interval=DEFAULT_HEDGER_INTERVAL,
    )
    trade_config = TradeConfig(
        exchange=cmi,
        cards=cards,
        pricer=pricer,
        future=future,
        call=call,
        put=put,
        hedger=hedger,
        mode=DEFAULT_MODE,
    )
    Thread(target=start_ui, args=(cmi, trade_config), daemon=True).start()
    if trade_config.mode == Mode.FULL_AUTO:
        full_auto_trade(trade_config)
    elif trade_config.mode == Mode.MANUAL_NEWS:
        manual_news_trade(trade_config)
    else:
        logger.fatal("Unknown mode")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        main()
    except Exception as error:
        cmi.delete_all_orders()
        logger.exception(error)
        logger.error(f"Exception thrown, cancelled all orders, quitting")
