import logging
import queue

from api import BearerAuth, send_order
from order import OrderRequest

logger = logging.getLogger(__name__)


def order_sender(queue: queue.Queue[OrderRequest], auth: BearerAuth):
    while True:
        order = queue.get()
        logger.info(f"Sending order {order}")
        send_order(auth, order)
        queue.task_done()


