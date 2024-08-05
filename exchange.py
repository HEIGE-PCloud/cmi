import queue
import threading
from typing import Dict, List, Optional
from api import get_all_products, sign_in, sign_up
import api
from connectivity import (
    ConnectivityRequest,
    ConnectivityRequestType,
    market_feeder,
    market_status,
    connectivity,
)
from model import (
    MarketStatus,
    OrderCriteria,
    OrderRequest,
    OrderStatus,
    PositionLimit,
    PriceBook,
    ProductResponse,
    Side,
)
from order_book import OrderBook


class Exchange:
    def __init__(
        self,
        username: str,
        password: str,
        sign_up_for_new_account=True,
    ):
        if sign_up_for_new_account:
            sign_up(username, password)
        self._auth = sign_in(username, password)
        self.products: Dict[str, ProductResponse] = {}
        self.update_products()

    def insert_order(
        self, instrument_id: str, *, price: float, volume: int, side: Side
    ):
        """
        Insert a limit order on an instrument.
        """
        api.send_order(
            self._auth,
            OrderRequest(side=side, price=price, volume=volume, product=instrument_id),
        )

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

    def get_outstanding_orders(self, instrument_id: str) -> Optional[Dict[str, OrderStatus]]:
        orders = api.get_current_orders(self._auth)
        if orders is None:
            return None
        res = {}
        for order in orders.root:
            res[order.id] = OrderStatus(order.product, order.id, order.price, order.volume, order.side)
        return res
    
    def get_last_price_book(self, instrument_id: str) -> PriceBook:
        order_book = api.get_order_book(self._auth, instrument_id)
        # TODO
        price_book = PriceBook()
        return price_book

    def get_positions(self) -> Dict[str, int]:
        # TODO
        return {}
    
    def get_pnl(self):
        # TODO
        pass
    
    def get_news(self):
        pass

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
