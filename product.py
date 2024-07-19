# [
#     {
#         "symbol": "75 C",
#         "tickSize": 0.1,
#         "startingPrice": 0,
#         "contractSize": 1
#     },
#     {
#         "symbol": "Sum",
#         "tickSize": 1,
#         "startingPrice": 0,
#         "contractSize": 1
#     },
#     {
#         "symbol": "65 P",
#         "tickSize": 0.1,
#         "startingPrice": 0,
#         "contractSize": 1
#     },
#     {
#         "symbol": "70 Straddle",
#         "tickSize": 0.25,
#         "startingPrice": 0,
#         "contractSize": 1
#     }
# ]


from typing import List
from pydantic import BaseModel, RootModel


class Product(BaseModel):
    symbol: str
    tickSize: float
    startingPrice: float
    contractSize: float


ProductList = RootModel[List[Product]]
