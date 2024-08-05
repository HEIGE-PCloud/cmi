import logging
import queue
import threading
import time
from enum import Enum
from typing import Dict, List

from api import BearerAuth, delete_order, delete_order_by_criteria, get_order_book, get_status, send_order
from model import MarketStatus
from order_book import OrderBook

logger = logging.getLogger(__name__)


class ConnectivityRequestType(Enum):
    NEW_ORDER = 0
    CANCEL_ORDER = 1
    CANCEL_ORDER_BY_CRITERIA = 2


class ConnectivityRequest:

    def __init__(self, type: ConnectivityRequestType, data) -> None:
        self.type = type
        self.data = data


def connectivity(queue: queue.Queue[ConnectivityRequest], auth: BearerAuth):
    while True:
        request = queue.get()
        if request.type == ConnectivityRequestType.NEW_ORDER:
            logger.info(f"Sending order {request.data}")
            send_order(auth, request.data)
        elif request.type == ConnectivityRequestType.CANCEL_ORDER:
            logger.info(f"Cancelling order {request.data}")
            delete_order(auth, request.data)
        elif request.type == ConnectivityRequestType.CANCEL_ORDER_BY_CRITERIA:
            delete_order_by_criteria(auth, request.data)
        queue.task_done()


def market_feeder(lock: threading.Lock, products: List[str], order_books: Dict[str, OrderBook], auth: BearerAuth, ):
    while True:
        for product in products:
            res = get_order_book(auth, product)
            if res is not None:
                with lock:
                    order_books[product] = res
        time.sleep(0.01)


def market_status(status: MarketStatus, auth: BearerAuth):
    success = False
    while True:

        res = get_status(auth)
        if res is None:
            success = False
        else:
            status.acceptingOrders = res.acceptingOrders
            status.activeRoundName = res.activeRoundName
            status.username = res.username
            status.userRanking = res.userRanking
            for product in res.positionLimits.root:
                status.positionLimits[product.productSymbol].longLimit = (product.longLimit)
                status.positionLimits[product.productSymbol].shortLimit = (product.shortLimit)
            success = True
        if success:
            time.sleep(1)
        else:
            time.sleep(0.01)
