from typing import List


class Cards:
    all_cards = [1.0, 1.0, 1.0, 1.0, 2.0, 2.0, 2.0, 2.0, 3.0, 3.0, 3.0, 3.0, 4.0, 4.0, 4.0, 4.0, 5.0, 5.0, 5.0, 5.0,
                 6.0, 6.0, 6.0, 6.0, 7.0, 7.0, 7.0, 7.0, 8.0, 8.0, 8.0, 8.0, 9.0, 9.0, 9.0, 9.0, 10.0, 10.0, 10.0, 10.0,
                 11.0, 11.0, 11.0, 11.0, 12.0, 12.0, 12.0, 12.0, 13.0, 13.0, 13.0, 13.0, ]

    def __init__(self, total_cards_to_choose=20):
        self._chosen_cards = []
        self._total_cards_to_choose = total_cards_to_choose

    def choose_card(self, card: float):
        self._chosen_cards.append(card)

    def get_chosen_cards_num(self) -> int:
        return len(self._chosen_cards)

    def set_chosen_cards(self, cards: List[float]):
        self._chosen_cards = cards

    def get_chosen_cards_sum(self) -> float:
        return sum(self._chosen_cards)

    def get_remaining_cards(self) -> List[float]:
        remaining_cards = self.all_cards.copy()
        for x in self._chosen_cards:
            remaining_cards.remove(x)
        return remaining_cards

    def get_remaining_cards_to_choose(self) -> int:
        return self._total_cards_to_choose - len(self._chosen_cards)

    def get_expected_value(self) -> float:
        cards = self.get_remaining_cards()
        return sum(cards) / len(cards)

    def get_theoretical_price(self) -> float:
        return self.get_expected_value() * self.get_remaining_cards_to_choose() + self.get_chosen_cards_sum()


def test_choose_cards():
    cards = Cards()
    cards.choose_card(1.0)
    cards.choose_card(2.0)
    cards.choose_card(3.0)
    assert cards._chosen_cards == [1.0, 2.0, 3.0]
    assert cards.get_remaining_cards() == [1.0, 1.0, 1.0, 2.0, 2.0, 2.0, 3.0, 3.0, 3.0, 4.0, 4.0, 4.0, 4.0, 5.0, 5.0,
                                           5.0, 5.0, 6.0, 6.0, 6.0, 6.0, 7.0, 7.0, 7.0, 7.0, 8.0, 8.0, 8.0, 8.0, 9.0,
                                           9.0, 9.0, 9.0, 10.0, 10.0, 10.0, 10.0, 11.0, 11.0, 11.0, 11.0, 12.0, 12.0,
                                           12.0, 12.0, 13.0, 13.0, 13.0, 13.0, ]
    assert cards.get_remaining_cards_to_choose() == 17


def test_choose_card():
    cards = Cards()
    cards.set_chosen_cards(cards.all_cards)
    assert cards.get_remaining_cards() == []


def test_theoretical_price():
    cards = Cards()
    cards.set_chosen_cards([1.0, 2.0, 3.0])
    assert cards.get_theoretical_price() == 1.0 + 2.0 + 3.0 + cards.get_expected_value() * 17

    cards2 = Cards()
    assert cards2.get_expected_value() == 7.0
    assert cards2.get_theoretical_price() == 140
