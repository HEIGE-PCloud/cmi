import queue
import threading
import time
from typing import Dict, List
from api import delete_order, delete_order_by_criteria, get_all_products, sign_in, sign_up
from connectivity import ConnectivityRequest, ConnectivityRequestType, market_feeder, market_status, connectivity
from model import MarketStatus, OrderCriteria, OrderRequest, PositionLimit, Side
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
        self._order_book_lock = threading.Lock()

        # Hitters setup
        self.update_products()

        # Market status setups
        self._market_status = MarketStatus()
        for product in self._products:
            self._market_status.positionLimits[product.symbol] = PositionLimit(shortLimit=0, longLimit=0)
        self._market_status_thread = threading.Thread(
            target=market_status,
            args=[
                self._market_status,
                self._auth
            ],
            daemon=True
        )
        self._market_status_thread.start()

        # Market feed setups
        self._order_book: Dict[str, OrderBook] = {}
        self._market_feed_thread = threading.Thread(
            target=market_feeder,
            args=[
                self._order_book_lock,
                self.get_products_symbols(),
                self._order_book,
                self._auth,
            ],
            daemon=True,
        )
        self._market_feed_thread.start()

        # Order sender setups
        self._connectivity_queue: queue.Queue[ConnectivityRequest] = queue.Queue()
        self._connectivity_thread = threading.Thread(
            target=connectivity,
            args=[self._connectivity_queue, self._auth],
            daemon=True,
        )
        self._connectivity_thread.start()

        # Order canceller setups
        self._order_canceller_queue: queue.Queue[None] = queue.Queue()

    def insert_order(self, order: OrderRequest):
        """
        Insert a limit order on an instrument.
        """
        self._connectivity_queue.put(ConnectivityRequest(type=ConnectivityRequestType.NEW_ORDER, data=order))

    def delete_order(self, id: str):
        """
        Delete a specific outstanding limit order on an instrument.
        """
        self._connectivity_queue.put(ConnectivityRequest(type=ConnectivityRequestType.CANCEL_ORDER, data=id))

    def delete_all_orders(self):
        """
        Delete all outstanding orders on an instrument.
        """
        for product in self._products:
            product.symbol
            self.delete_all_orders_for_symbol(product.symbol)

    def delete_all_orders_for_symbol(self, symbol: str):
        self._connectivity_queue.put(ConnectivityRequest(type=ConnectivityRequestType.CANCEL_ORDER_BY_CRITERIA, data=OrderCriteria(product=symbol, side=Side.BUY, price=None)))
        self._connectivity_queue.put(ConnectivityRequest(type=ConnectivityRequestType.CANCEL_ORDER_BY_CRITERIA, data=OrderCriteria(product=symbol, side=Side.SELL, price=None)))

    def get_products(self):
        """
        Return all products on the exchange.
        """
        return self._products

    def get_products_symbols(self) -> List[str]:
        """
        Return a list of product symbol names
        """
        return [product.symbol for product in self._products]

    def update_products(self):
        """
        Update all products on the exchange.
        """
        self._products = get_all_products(self._auth).root

    def verify_hitters(self):
        symbols = self.get_products_symbols()
        for hitter in self._hitters:
            assert (
                hitter.get_symbol() in symbols
            ), f"Invalid hitter: {hitter.get_symbol()}, valid products: {self.get_products_symbols()}"
            for product in self._products:
                if product.symbol == hitter.get_symbol():
                    hitter.init(
                        self._order_book_lock,
                        product.tickSize,
                        product.startingPrice,
                        product.contractSize,
                    )
                    break

    def get_rank(self) -> int:
        return self._market_status.userRanking
                
    def join(self):
        self._connectivity_thread.join()

if __name__ == '__main__':
    USERNAME = "test2"
    PASSWORD = "test2"
    cmi = Exchange(USERNAME, PASSWORD, sign_up_for_new_account=False)
