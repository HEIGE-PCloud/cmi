from json import JSONDecodeError
from typing import Optional
import requests
import urllib3
import logging

from model import NewsResponseList, OrderCriteria, OrderRequest, OrderList, PositionResponseList, Side, StatusResponse
from order_book import OrderBook
from model import ProductResponseList

logger = logging.getLogger(__name__)

urllib3.disable_warnings(category=urllib3.exceptions.InsecureRequestWarning)

s = requests.Session()


class BearerAuth(requests.auth.AuthBase):
    def __init__(self, token: str):
        self.token = token

    def __call__(self, req):
        req.headers["authorization"] = self.token
        return req


ENDPOINT = "https://staging-cmi-exchange/api"


def ensure_success(response: requests.Response, message: str, *, fail_hard=False):
    if response.ok:
        return True
    try:
        error_message = f"{message}\n{response.json()["message"]}"
    except JSONDecodeError:
        error_message = response.text

    if fail_hard:
        raise Exception(error_message)
    else:
        logger.error(error_message)
        return False


def sign_up(username: str, password: str):
    path = "/user"
    logger.debug(f"Signing up with username: {username} password: {password}")
    res = s.post(
        ENDPOINT + path, json={"username": username, "password": password}, verify=False
    )
    ensure_success(res, "Sign up failed!", fail_hard=True)
    json = res.json()
    assert json.username == username
    logger.info("Signing up success")


def sign_in(username: str, password: str) -> BearerAuth:
    path = "/user/authenticate"
    logger.debug(f"Signing in with username: {username} password: {password}")
    res = s.post(
        ENDPOINT + path, json={"username": username, "password": password}, verify=False
    )
    ensure_success(res, "Sign in failed!", fail_hard=True)
    bearer_token = res.headers["Authorization"]
    logger.info(f"Signing in success with bearer token {bearer_token}")
    return BearerAuth(bearer_token)


def get_status(auth: BearerAuth) -> Optional[StatusResponse]:
    path = "/status"
    logger.debug(f"Getting status")
    res = s.get(
        ENDPOINT + path, auth=auth, verify=False
    )
    if ensure_success(res, "Getting status failed!"):
        status = StatusResponse(**res.json())
        logger.debug(f"Getting status success: {status}")
        return status
    return None


def get_all_products(auth: BearerAuth) -> ProductResponseList:
    path = "/product"
    logger.debug(f"Getting products")
    res = s.get(ENDPOINT + path, auth=auth, verify=False)
    ensure_success(res, "Get product failed!", fail_hard=True)
    product_list = ProductResponseList(res.json())
    logger.debug(f"Getting product list success: {product_list}")
    return product_list


def get_order_book(auth: BearerAuth, product_name: str) -> Optional[OrderBook]:
    path = f"/product/{product_name}/order-book/current-user"
    logger.debug(f"Getting the order book for product: {product_name}")
    res = s.get(ENDPOINT + path, auth=auth, verify=False)
    if ensure_success(res, "Get order book failed!"):
        order_book = OrderBook(**res.json())
        logger.debug(f"Getting order book success: {order_book}")
        return order_book
    return None


def send_order(auth: BearerAuth, order: OrderRequest):
    path = "/order"
    logger.debug(f"Sending new order: {order}")
    res = s.post(ENDPOINT + path, json=order.model_dump(), auth=auth, verify=False)
    if ensure_success(res, "Failed to send new order"):
        logger.debug("Sending new order success")


def get_current_orders(auth: BearerAuth) -> Optional[OrderList]:
    path = "/order/current-user"
    logger.debug("Getting current orders")
    res = s.get(ENDPOINT + path, auth=auth, verify=False)
    if ensure_success(res, "Get current orders failed!"):
        order_list = OrderList(res.json())
        logger.debug(f"Getting current orders success: {order_list}")
        return order_list
    return None


def delete_order(auth: BearerAuth, order_id: str):
    path = f"/order/{order_id}"
    logger.debug(f"Deleting order {order_id}")
    res = s.delete(ENDPOINT + path, auth=auth, verify=False)
    if ensure_success(res, "Delete order failed!"):
        logger.debug("Deleting order success")


def delete_order_by_criteria(auth: BearerAuth, criteria: OrderCriteria):
    path = f"/order"
    logger.debug(f"Delete order by criteria")
    res = s.delete(ENDPOINT + path, params=criteria.model_dump(), auth=auth, verify=False)
    ensure_success(res, "Delete order by criteria failed!")


def get_position(auth: BearerAuth):
    path = "/position/current-user"
    logger.debug("Getting position")
    res = s.get(ENDPOINT + path, auth=auth, verify=False)
    if ensure_success(res, "Get position failed!"):
        positions = PositionResponseList(res.json())
        logger.debug(f"Getting position success: {positions}")
        return positions
    return None


def get_news(auth: BearerAuth):
    path = "/news"
    logger.debug("Getting news")
    res = s.get(ENDPOINT + path, auth=auth, verify=False)
    if ensure_success(res, "Get news failed!"):
        news = NewsResponseList(res.json())
        logger.debug(f"Getting news success: {news}")
        return news
    return None


def main():
    auth = sign_in("test", "test")
    product_list = get_all_products(auth)
    product0 = product_list.root[0]
    get_order_book(auth, product0.symbol)
    send_order(auth, OrderRequest(side=Side.BUY, price=0, volume=1, product=product0.symbol))
    get_current_orders(auth)
    delete_order(auth, "1")
    delete_order_by_criteria(auth, OrderCriteria(product=None, price=None, side=None))


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main()
