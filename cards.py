from typing import List


class Cards:
    all_cards = [
        1.0,
        1.0,
        1.0,
        1.0,
        2.0,
        2.0,
        2.0,
        2.0,
        3.0,
        3.0,
        3.0,
        3.0,
        4.0,
        4.0,
        4.0,
        4.0,
        5.0,
        5.0,
        5.0,
        5.0,
        6.0,
        6.0,
        6.0,
        6.0,
        7.0,
        7.0,
        7.0,
        7.0,
        8.0,
        8.0,
        8.0,
        8.0,
        9.0,
        9.0,
        9.0,
        9.0,
        10.0,
        10.0,
        10.0,
        10.0,
        11.0,
        11.0,
        11.0,
        11.0,
        12.0,
        12.0,
        12.0,
        12.0,
        13.0,
        13.0,
        13.0,
        13.0,
    ]

    def __init__(self):
        self._chosen_cards = []

    def choose_card(self, card: float):
        self._chosen_cards.append(card)

    def set_chosen_cards(self, cards: List[float]):
        self._chosen_cards = cards

    def get_remaining_cards(self) -> List[float]:
        remaining_cards = self.all_cards.copy()
        for x in self._chosen_cards:
            remaining_cards.remove(x)
        return remaining_cards


def test_choose_cards():
    cards = Cards()
    cards.choose_card(1.0)
    cards.choose_card(2.0)
    cards.choose_card(3.0)
    assert cards._chosen_cards == [1.0, 2.0, 3.0]
    assert cards.get_remaining_cards() == [
        1.0,
        1.0,
        1.0,
        2.0,
        2.0,
        2.0,
        3.0,
        3.0,
        3.0,
        4.0,
        4.0,
        4.0,
        4.0,
        5.0,
        5.0,
        5.0,
        5.0,
        6.0,
        6.0,
        6.0,
        6.0,
        7.0,
        7.0,
        7.0,
        7.0,
        8.0,
        8.0,
        8.0,
        8.0,
        9.0,
        9.0,
        9.0,
        9.0,
        10.0,
        10.0,
        10.0,
        10.0,
        11.0,
        11.0,
        11.0,
        11.0,
        12.0,
        12.0,
        12.0,
        12.0,
        13.0,
        13.0,
        13.0,
        13.0,
    ]

def test_choose_card():
  cards = Cards()
  cards.set_chosen_cards(cards.all_cards)
  assert cards.get_remaining_cards() == []
