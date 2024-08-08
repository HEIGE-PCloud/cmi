from typing import List
from model import NewsResponse
from trade_config import TradeConfig


def news_to_cards(news: List[NewsResponse]):
    cards = []
    for new in news:
        res = new.to_card()
        if res is not None:
            cards.append(res)
    return cards


def trade(config: TradeConfig):
    while True:
        news = config.exchange.get_news()
        cards = news_to_cards(news)
        size = len(cards)
        if size != config.cards.get_chosen_cards_num():
            config.update_cards(news_to_cards(news))

        for strategy in config.strategies:
            strategy.make_market()

        config.hedger.hedge(config.cards.get_theoretical_price())
