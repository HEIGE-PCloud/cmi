import requests
import urllib3
import logging

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


def log_in(username: str, password: str):
    PATH = "/user/authenticate"
    logger.info(f"Logging in with username: {username} password: {password}")
    res = requests.post(
        ENDPOINT + PATH, json={"username": username, "password": password}, verify=False
    )
    ensure_success(res, "Log in failed!")
    bearer_token = res.headers["Authorization"]
    logger.info(f"Logging in success with bearer token {bearer_token}")
    return bearer_token


def get_product(auth: BearerAuth):
    PATH = "/product"
    res = requests.get(ENDPOINT + PATH, auth=auth, verify=False)
    ensure_success(res, "Get product failed!")
    print(res.json())


def main():
    bearer_token = log_in("test4", "test4")
    auth = BearerAuth(bearer_token)
    get_product(auth)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
