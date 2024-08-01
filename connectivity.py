from enum import Enum
import logging
import queue
import threading
import time
from typing import Any, Dict, List

from api import BearerAuth, delete_order, delete_order_by_criteria, get_order_book, get_status, send_order
from model import MarketStatus, OrderRequest
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
        if  request.type == ConnectivityRequestType.NEW_ORDER:
            logger.info(f"Sending order {request.data}")
            send_order(auth, request.data)
        elif request.type == ConnectivityRequestType.CANCEL_ORDER:
            logger.info(f"Cancelling order {request.data}")
            delete_order(auth, request.data)
        elif request.type == ConnectivityRequestType.CANCEL_ORDER_BY_CRITERIA:
            delete_order_by_criteria(auth, request.data)
        queue.task_done()


def market_feeder(
    lock: threading.Lock,
    products: List[str],
    order_books: Dict[str, OrderBook],
    auth: BearerAuth,
):
    while True:
        for product in products:
            res = get_order_book(auth, product)
            if res is not None:
                with lock:
                    order_books[product] = res
        time.sleep(0.01)


def market_status(market_status: MarketStatus, auth: BearerAuth):
    success = False
    while True:

        res = get_status(auth)
        if res is None:
            success = False
        else:
            market_status.acceptingOrders = res.acceptingOrders
            market_status.activeRoundName = res.activeRoundName
            market_status.username = res.username
            market_status.userRanking = res.userRanking
            for product in res.positionLimits.root:
                market_status.positionLimits[product.productSymbol].longLimit = (
                    product.longLimit
                )
                market_status.positionLimits[product.productSymbol].shortLimit = (
                    product.shortLimit
                )
            success = True
        if success:
            time.sleep(1)
        else:
            time.sleep(0.01)
