from api import delete_order, get_all_products, send_order, sign_in, sign_up
from order import OrderRequest


class Exchange:
    def __init__(self, username: str, password: str, sign_up_for_new_account=True):
        if sign_up_for_new_account:
            sign_up(username, password)
        self.auth = sign_in(username, password)
        self.update_products()

    def insert_order(self, order: OrderRequest):
        """
        Insert a limit order on an instrument.
        """
        send_order(self.auth, order)

    def delete_order(self, id: str):
        """
        Delete a specific outstanding limit order on an instrument.
        """
        delete_order(self.auth, id)

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
        self.products = get_all_products(self.auth)
