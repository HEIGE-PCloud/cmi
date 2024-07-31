from cards import Cards
from option_pricing import compile_option_pricing_cpp, option_pricing_cpp


class TradeConfig():
    
    def __init__(self) -> None:
        compile_option_pricing_cpp()
        self.cards = Cards()
        self.get_cards_value = None
        self.future_theo = None
        self.call_theo = None
        self.put_theo = None
        self.call_delta = None
        self.put_delta = None
        self.threads = 4
        self.iterations = 300000
        self.update_theo()        

    def update_cards(self):
        self.cards.set_chosen_cards(self.get_cards_value())
        self.update_theo()

    def update_theo(self):
        self.future_theo = self.cards.get_theoretical_price()
        self.call_theo, self.put_theo, self.call_delta, self.put_delta = option_pricing_cpp(self.cards, self.threads, self.iterations)    
    
    def reset_theo(self):
        self.call_theo = None
        self.put_theo = None
        self.call_delta = None
        self.put_delta = None
        self.future_theo = None