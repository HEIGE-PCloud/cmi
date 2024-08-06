from model import NewsResponseList
from trade_config import TradeConfig


def news_to_cards(news: NewsResponseList):
    cards = []
    for new in news.root:
        cards.append(new.to_card())
    return cards


def trade(config: TradeConfig):
    while True:
        news = config.exchange.get_news()
        if news is not None:
            size = len(news.root)
            if size == config.cards.get_chosen_cards_num():
                for strategy in config.strategies:
                    strategy.make_market()
            else:
                config.update_cards(news_to_cards(news))
        else:
            config.exchange.delete_all_orders()

        config.hedge.hedge(config.cards.get_theoretical_price())
