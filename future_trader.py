
from cards import Cards
from exchange import Exchange
from model import Side
from trade import news_to_cards
from util import round_down_to_tick, round_up_to_tick
import logging

logger = logging.getLogger(__name__)

def main():
    cmi = Exchange("FutureTrader", "FutureTrader", sign_up_for_new_account=False)
    cards = Cards()
    while True:
        news = cmi.get_news()
        if news is not None:
            size = len(news.root)
            if size == cards.get_chosen_cards_num():
                pass
            else:
                cards.set_chosen_cards(news_to_cards(news))
                cmi.delete_all_orders()
                theo = cards.get_theoretical_price()
                bid_price = round_down_to_tick(theo, 0.5)
                ask_price = round_up_to_tick(theo, 0.5)
                if bid_price == ask_price:
                    ask_price += 0.5
                logging.info(f"Making market at {bid_price} - {ask_price}")
                cmi.insert_order("FUTURE", price=bid_price, volume=200, side=Side.BUY)
                cmi.insert_order("FUTURE", price=ask_price, volume=200, side=Side.SELL)
        else:
            logging.info("Delete all orders")
            cmi.delete_all_orders()
    
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()