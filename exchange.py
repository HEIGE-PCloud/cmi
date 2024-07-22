import queue
import threading
from api import delete_order, get_all_products, sign_in, sign_up
from connectivity import order_sender
from order import OrderRequest


class Exchange:
    def __init__(self, username: str, password: str, sign_up_for_new_account=True):
        if sign_up_for_new_account:
            sign_up(username, password)
        self._auth = sign_in(username, password)
        self.update_products()
        self._order_sender_queue: queue.Queue[OrderRequest] = queue.Queue()
        self._order_canceller_queue: queue.Queue[None] = queue.Queue()
        self._order_sender_thread = threading.Thread(
            target=order_sender, args=[self._order_sender_queue, self._auth], daemon=True
        )
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
        return self.products

    def update_products(self):
        """
        Update all products on the exchange.
        """
        self.products = get_all_products(self._auth)
        
    def join(self):
        self._order_sender_queue.join()
