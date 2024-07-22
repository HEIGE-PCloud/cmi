import queue
import threading
from typing import Dict, List
from api import delete_order, get_all_products, sign_in, sign_up
from connectivity import market_feeder, order_sender
from order import OrderRequest
from order_book import OrderBook


class Exchange:
    def __init__(self, username: str, password: str, sign_up_for_new_account=True):
        if sign_up_for_new_account:
            sign_up(username, password)
        self._auth = sign_in(username, password)
        self.update_products()
        self._order_sender_queue: queue.Queue[OrderRequest] = queue.Queue()
        self._order_canceller_queue: queue.Queue[None] = queue.Queue()
        self._order_sender_thread = threading.Thread(
            target=order_sender,
            args=[self._order_sender_queue, self._auth],
            daemon=True,
        )
        self._order_book: Dict[str, OrderBook] = {}
        self._market_feed_thread = threading.Thread(
            target=market_feeder,
            args=[self.get_products_symbols(), self._order_book, self._auth],
            daemon=True,
        )
        self._market_feed_thread.start()
        self._order_sender_thread.start()

    def insert_order(self, order: OrderRequest):
        """
        Insert a limit order on an instrument.
        """
        self._order_sender_queue.put(order)

    def delete_order(self, id: str):
        """
        Delete a specific outstanding limit order on an instrument.
        """
        delete_order(self._auth, id)

    def delete_all_orders(self):
        """
        Delete all outstanding orders on an instrument.
        """
        pass

    def get_products(self):
        """
        Return all products on the exchange.
        """
        return self._products

    def get_products_symbols(self) -> List[str]:
        """
        Return a list of product symbol names
        """
        return [product.symbol for product in self._products.root]

    def update_products(self):
        """
        Update all products on the exchange.
        """
        self._products = get_all_products(self._auth)

    def join(self):
        self._order_sender_queue.join()
        self._market_feed_thread.join()
