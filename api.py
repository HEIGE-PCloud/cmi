import requests
import urllib3
import logging

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


def ensure_success(response: requests.Response, message: str):
    assert response.ok, f"{message}\n{response.json()["message"]}"


def sign_up(username: str, password: str):
    PATH = "/user"
    logger.info(f"Signing up with username: {username} password: {password}")
    res = requests.post(
        ENDPOINT + PATH, json={"username": username, "password": password}, verify=False
    )
    ensure_success(res, "Sign up failed!")
    json = res.json()
    assert json.username == username
    logger.info("Signing up success")


def sign_in(username: str, password: str) -> BearerAuth:
    PATH = "/user/authenticate"
    logger.info(f"Signing in with username: {username} password: {password}")
    res = requests.post(
        ENDPOINT + PATH, json={"username": username, "password": password}, verify=False
    )
    ensure_success(res, "Sign in failed!")
    bearer_token = res.headers["Authorization"]
    logger.info(f"Signing in success with bearer token {bearer_token}")
    return BearerAuth(bearer_token)


def get_product(auth: BearerAuth) -> ProductList:
    PATH = "/product"
    logger.info(f"Getting products")
    res = requests.get(ENDPOINT + PATH, auth=auth, verify=False)
    ensure_success(res, "Get product failed!")
    product_list = ProductList(res.json())
    logger.info(f"Getting product list success: {product_list}")
    return product_list


def get_order_book(auth: BearerAuth, product_name: str) -> OrderBook:
    PATH = f"/product/{product_name}/order-book/current-user"
    logger.info(f"Getting the order book for product: {product_name}")
    res = requests.get(ENDPOINT + PATH, auth=auth, verify=False)
    ensure_success(res, "Get order book failed!")
    order_book = OrderBook(**res.json())
    logger.info(f"Getting order book success: {order_book}")
    return order_book


def main():
    auth = sign_in("test4", "test4")
    product_list = get_product(auth)
    product0 = product_list.root[0]
    get_order_book(auth, product0.symbol)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
