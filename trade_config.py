from typing import List
from cards import Cards
from option_pricing import compile_option_pricing_cpp, option_pricing_cpp
import threading
import queue


class TradeConfig():
    
    def __init__(self) -> None:
        compile_option_pricing_cpp()
        self.pricing = Pricing(self)
        self.cards = Cards()
        self.get_cards_value = None
        self.future_theo = None
        self.call_theo = None
        self.put_theo = None
        self.call_delta = None
        self.put_delta = None
        self.threads = 10
        self.iterations = 500000
        self.update_theo()        
    def with_strategies(self, strategies):
        self.strategies = strategies

    def update_cards(self):
        self.reset_theo()
        self.cards.set_chosen_cards(self.get_cards_value())
        self.update_theo()

    def update_theo(self):
        self.future_theo = self.cards.get_theoretical_price()
        self.pricing.pricing()
    
    def reset_theo(self):
        self.call_theo = None
        self.put_theo = None
        self.call_delta = None
        self.put_delta = None
        self.future_theo = None

class Pricing():

    def __init__(self, config: TradeConfig) -> None:
        self.config = config
        self.queue = queue.Queue()
        self.pricing_thread = threading.Thread(target=self.option_pricing_cpp_thread, daemon=True)
        self.pricing_thread.start()

    def option_pricing_cpp_thread(self):

        while True:
            x = self.queue.get()
            self.config.call_theo, self.config.put_theo, self.config.call_delta, self.config.put_delta = option_pricing_cpp(self.config.cards, self.config.threads, self.config.iterations)
            self.queue.task_done()
    
    def pricing(self):
        self.queue.put(1)
