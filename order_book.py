# {
#     "product": "75 C",
#     "tickSize": 0.1,
#     "midPrice": 0,
#     "buy": [
#         {
#             "price": 3,
#             "volume": 4
#         }
#     ],
#     "sell": [
#         {
#             "price": 5,
#             "volume": 100
#         }
#     ]
# }
from typing import List
from pydantic import BaseModel, RootModel


class BuyOrder(BaseModel):
    price: float
    volume: int


BuyOrderList = RootModel[List[BuyOrder]]


class SellOrder(BaseModel):
    price: float
    volume: int


SellOrderList = RootModel[List[SellOrder]]


class OrderBook(BaseModel):
    product: str
    tickSize: float
    midPrice: float
    buy: BuyOrderList
    sell: SellOrderList
