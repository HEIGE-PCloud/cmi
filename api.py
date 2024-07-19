import requests
import urllib3
import logging

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
    if not response.ok:
        raise Exception(message + "\n" + response.json()["message"])


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


def log_in(username: str, password: str) -> BearerAuth:
    PATH = "/user/authenticate"
    logger.info(f"Logging in with username: {username} password: {password}")
    res = requests.post(
        ENDPOINT + PATH, json={"username": username, "password": password}, verify=False
    )
    ensure_success(res, "Log in failed!")
    bearer_token = res.headers["Authorization"]
    logger.info(f"Logging in success with bearer token {bearer_token}")
    return BearerAuth(bearer_token)


def get_product(auth: BearerAuth) -> ProductList:
    PATH = "/product"
    res = requests.get(ENDPOINT + PATH, auth=auth, verify=False)
    ensure_success(res, "Get product failed!")
    product_list = ProductList(res.json())
    return product_list


def main():
    auth = log_in("test4", "test4")
    product_list = get_product(auth)
    print(product_list)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
