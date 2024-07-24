import logging
import queue
import threading
import time
from typing import Dict, List

from api import BearerAuth, get_order_book, send_order
from model import OrderRequest
from order_book import OrderBook

logger = logging.getLogger(__name__)


def order_sender(queue: queue.Queue[OrderRequest], auth: BearerAuth):
    while True:
        order = queue.get()
        logger.info(f"Sending order {order}")
        send_order(auth, order)
        queue.task_done()


def market_feeder(lock: threading.Lock, products: List[str], order_books: Dict[str, OrderBook], auth: BearerAuth):
    while True:
        for product in products:
            res = get_order_book(auth, product)
            if res is not None:
                with lock:
                    order_books[product] = res
        time.sleep(0.01)
