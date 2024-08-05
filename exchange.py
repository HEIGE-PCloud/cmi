import datetime
from typing import Dict, List, Optional

import api
from api import get_all_products, sign_in, sign_up
from model import (OrderCriteria, OrderRequest, OrderStatus, PriceBook, PriceVolume, ProductResponse, Side, )


class Exchange:
    def __init__(self, username: str, password: str, sign_up_for_new_account=True, ):
        if sign_up_for_new_account:
            sign_up(username, password)
        self._auth = sign_in(username, password)
        self.products: Dict[str, ProductResponse] = {}
        self.update_products()
        self.delete_all_orders()

    def insert_order(self, instrument_id: str, *, price: float, volume: int, side: Side):
        """
        Insert a limit order on an instrument.
        """
        return api.send_order(self._auth, OrderRequest(side=side, price=price, volume=volume, product=instrument_id))

    def insert_ioc_order(self, instrument_id: str, price: float, volume: int, side: Side):
        res = api.send_order(self._auth, OrderRequest(side=side, price=price, volume=volume, product=instrument_id))
        if res is not None:
            self.delete_order(res.id)

    def delete_order(self, order_id: str):
        """
        Delete a specific outstanding limit order on an instrument.
        """
        api.delete_order(self._auth, order_id)

    def delete_orders(self, instrument_id: str):
        api.delete_order_by_criteria(self._auth, OrderCriteria(product=instrument_id, side=Side.BUY, price=None))
        api.delete_order_by_criteria(self._auth, OrderCriteria(product=instrument_id, side=Side.SELL, price=None))

    def delete_all_orders(self):
        for product in self.products:
            self.delete_orders(product)

    def get_outstanding_orders(self, ) -> Optional[Dict[str, OrderStatus]]:
        orders = api.get_current_orders(self._auth)
        if orders is None:
            return None
        res = {}
        for order in orders.root:
            res[order.id] = OrderStatus(order.product, order.id, order.price, order.volume, order.side)
        return res

    def get_last_price_book(self, instrument_id: str) -> Optional[PriceBook]:
        order_book = api.get_order_book(self._auth, instrument_id)
        if order_book is None:
            return None
        bids: List[PriceVolume] = []
        asks: List[PriceVolume] = []
        buys = order_book.buy.root
        sells = order_book.sell.root
        for buy in buys:
            bids.append(PriceVolume(price=buy.price, volume=buy.volume))
        for sell in sells:
            asks.append(PriceVolume(price=sell.price, volume=sell.volume))
        bids.sort(key=lambda bid: bid.price, reverse=True)
        asks.sort(key=lambda ask: ask.price, reverse=False)
        price_book = PriceBook(timestamp=datetime.datetime.now(), instrument_id=instrument_id, bids=bids, asks=asks, )
        return price_book

    def get_positions(self) -> Optional[Dict[str, int]]:
        positions = api.get_position(self._auth)
        if positions is None:
            return None
        res = {}
        for position in positions.root:
            res[position.product] = position.volume
        return res

    def get_news(self):
        return api.get_news(self._auth)

    def get_product(self, product: str) -> ProductResponse:
        """
        Return all products on the exchange.
        """
        return self.products[product]

    def update_products(self) -> None:
        """
        Update all products on the exchange.
        """
        products = get_all_products(self._auth).root
        for product in products:
            self.products[product.symbol] = product

    def get_rank(self) -> Optional[int]:
        res = api.get_status(self._auth)
        if res is None:
            return None
        return res.userRanking


if __name__ == "__main__":
    USERNAME = "test2"
    PASSWORD = "test2"
    cmi = Exchange(USERNAME, PASSWORD, sign_up_for_new_account=False)
