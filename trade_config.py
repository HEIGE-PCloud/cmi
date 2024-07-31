from cards import Cards


class TradeConfig():
    
    def __init__(self) -> None:
        self.cards = Cards()
        self.get_cards_value = None
    
    def update_cards(self):
        self.cards.set_chosen_cards(self.get_cards_value())
    
    