from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, RootModel


class Side(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


# {"side": "BUY", "price": 1.4, "volume": 1, "product": "75 C"}
class OrderRequest(BaseModel):
    side: Side
    price: float
    volume: int
    product: str


class OrderResponse(BaseModel):
    id: str
    side: Side
    price: float
    volume: int
    product: str


class OrderCriteria(BaseModel):
    product: Optional[str]
    price: Optional[float]
    side: Optional[Side]


allOrders = OrderCriteria(product=None, price=None, side=None)
productOrders = lambda product: OrderCriteria(product=product, price=None, side=None)

OrderList = RootModel[List[OrderResponse]]


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


class ProductResponse(BaseModel):
    symbol: str
    tickSize: float
    startingPrice: float
    contractSize: float


ProductResponseList = RootModel[List[ProductResponse]]


# {
#     "activeRoundName": "Cards 2",
#     "acceptingOrders": false,
#     "username": "test1",
#     "userRanking": 17,
#     "positionLimits": [
#         {
#             "productSymbol": "65 P",
#             "shortLimit": 100,
#             "longLimit": 100
#         },
#         {
#             "productSymbol": "75 C",
#             "shortLimit": 100,
#             "longLimit": 100
#         },
#         {
#             "productSymbol": "70 Straddle",
#             "shortLimit": 100,
#             "longLimit": 100
#         },
#         {
#             "productSymbol": "Sum",
#             "shortLimit": 50,
#             "longLimit": 50
#         }
#     ]
# }


class PositionLimitResponse(BaseModel):
    productSymbol: str
    shortLimit: int
    longLimit: int


PositionLimitList = RootModel[List[PositionLimitResponse]]


class StatusResponse(BaseModel):
    activeRoundName: str
    acceptingOrders: bool
    username: str
    userRanking: int
    positionLimits: PositionLimitList


class PositionLimit(BaseModel):
    shortLimit: int
    longLimit: int


class MarketStatus(BaseModel):
    activeRoundName: str = "Default Roundname"
    acceptingOrders: bool = False
    username: str = "Default Username"
    userRanking: int = 0
    positionLimits: Dict[str, PositionLimit] = {}
