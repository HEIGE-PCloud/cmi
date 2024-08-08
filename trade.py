from typing import List
from model import NewsResponse
from trade_config import ManualNewsState, Mode, TradeConfig


def news_to_cards(news: List[NewsResponse]) -> List[int]:
    cards = []
    for new in news:
        res = new.to_card()
        if res is not None:
            cards.append(res)
    return cards


def full_auto_trade(config: TradeConfig):
    assert config.mode == Mode.FULL_AUTO
    while True:
        news = config.exchange.get_news()
        cards = news_to_cards(news)
        size = len(cards)
        
        if size != config.cards.get_chosen_cards_num():
            config.update_cards(cards)

        config.future.make_market()
        config.call.make_market()
        config.put.make_market()

        config.hedger.hedge(config.cards.get_theoretical_price())

def manual_news_trade(config: TradeConfig):
    assert config.mode == Mode.MANUAL_NEWS
    while True:
        match config.manul_news_state:
            case ManualNewsState.PAUSE:
                config.exchange.delete_all_orders()
            case ManualNewsState.TRADE:
                config.future.make_market()
                config.call.make_market()
                config.put.make_market()
            case ManualNewsState.HEDGE:
                config.hedger.hedge(config.cards.get_theoretical_price())
