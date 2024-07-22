class Hitter:
    def __init__(self, symbol: str, low_price: float, high_price: float) -> None:
        self._symbol = symbol
        self._low_price = low_price
        self._high_price = high_price

    def get_symbol(self) -> str:
        return self._symbol

    def init(self, tick_size: float, starting_price: float, contract_size: float) -> None:
        self._tick_size = tick_size
        self._starting_price = starting_price
        self._contract_size = contract_size

    def set_low_price(self, new_price: float) -> None:
        if new_price < self._high_price:
            self._low_price = new_price

    def set_high_price(self, new_price: float) -> None:
        if new_price > self._low_price:
            self._high_price = new_price
