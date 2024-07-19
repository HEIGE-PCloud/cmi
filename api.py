from json import JSONDecodeError
from typing import Optional
import requests
import urllib3
import logging

from order import OrderRequest, OrderList, Side
from order_book import OrderBook
from product import ProductList

logger = logging.getLogger(__name__)

urllib3.disable_warnings(category=urllib3.exceptions.InsecureRequestWarning)


class BearerAuth(requests.auth.AuthBase):
    def __init__(self, token: str):
        self.token = token

    def __call__(self, req):
        req.headers["authorization"] = self.token
        return req


ENDPOINT = "https://cmi-exchange/api"


def ensure_success(response: requests.Response, message: str, *, fail_hard = False):
    if response.ok:
        return True
    error_message = message
    try:    
        error_message = f"{message}\n{response.json()["message"]}"
    except JSONDecodeError:
        pass

    if fail_hard:
        raise Exception(error_message)
    else:
        logger.error(error_message)
        return False


def sign_up(username: str, password: str):
    PATH = "/user"
    logger.info(f"Signing up with username: {username} password: {password}")
    res = requests.post(
        ENDPOINT + PATH, json={"username": username, "password": password}, verify=False
    )
    ensure_success(res, "Sign up failed!", fail_hard=True)
    json = res.json()
    assert json.username == username
    logger.info("Signing up success")


def sign_in(username: str, password: str) -> BearerAuth:
    PATH = "/user/authenticate"
    logger.info(f"Signing in with username: {username} password: {password}")
    res = requests.post(
        ENDPOINT + PATH, json={"username": username, "password": password}, verify=False
    )
    ensure_success(res, "Sign in failed!", fail_hard=True)
    bearer_token = res.headers["Authorization"]
    logger.info(f"Signing in success with bearer token {bearer_token}")
    return BearerAuth(bearer_token)


def get_all_products(auth: BearerAuth) -> ProductList:
    PATH = "/product"
    logger.info(f"Getting products")
    res = requests.get(ENDPOINT + PATH, auth=auth, verify=False)
    ensure_success(res, "Get product failed!", fail_hard=True)
    product_list = ProductList(res.json())
    logger.info(f"Getting product list success: {product_list}")
    return product_list


def get_order_book(auth: BearerAuth, product_name: str) -> Optional[OrderBook]:
    PATH = f"/product/{product_name}/order-book/current-user"
    logger.info(f"Getting the order book for product: {product_name}")
    res = requests.get(ENDPOINT + PATH, auth=auth, verify=False)
    if ensure_success(res, "Get order book failed!"):
        order_book = OrderBook(**res.json())
        logger.info(f"Getting order book success: {order_book}")
        return order_book
    return None

def send_order(auth: BearerAuth, order: OrderRequest):
    PATH = "/order"
    logger.info(f"Sending new order: {order}")
    res = requests.post(ENDPOINT + PATH, json=order.model_dump(), auth=auth, verify=False)
    if ensure_success(res, "Failed to send new order"):
        logger.info("Sending new order success") 

def get_current_orders(auth: BearerAuth) -> Optional[OrderList]:
    PATH = "/order/current-user"
    logger.info("Getting current orders")
    res = requests.get(ENDPOINT + PATH, auth=auth, verify=False)
    if ensure_success(res, "Get current orders failed!"):        
        order_list = OrderList(res.json())
        logger.info(f"Getting current orders success: {order_list}")
        return order_list
    return None

def delete_order(auth: BearerAuth, id: str):
    PATH = f"/order/{id}"
    logger.info(f"Deleting order {id}")
    res = requests.delete(ENDPOINT + PATH, auth=auth, verify=False)
    if ensure_success(res, "Delete order failed!"):
        logger.info("Deleting order success")

def main():
    auth = sign_in("Junrong", "ads100")
    product_list = get_all_products(auth)
    product0 = product_list.root[0]
    get_order_book(auth, product0.symbol)
    send_order(auth, OrderRequest(side=Side.BUY, price=0, volume=1, product=product0.symbol))
    get_current_orders(auth)
    delete_order(auth, "1")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
