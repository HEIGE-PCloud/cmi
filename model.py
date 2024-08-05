import datetime
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
    status: str
    product: str
    side: Side
    price: float
    volume: int
    filled: int
    message: str
    user: str
    timestamp: datetime.datetime


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


# [
#   {
#     "time": "2024-08-05T16:13:56.704080677Z",
#     "message": "7"
#   },
#   {
#     "time": "2024-08-05T16:13:46.675778293Z",
#     "message": "A"
#   },
#   {
#     "time": "2024-08-05T16:13:36.648905531Z",
#     "message": "10"
#   },
#   {
#     "time": "2024-08-05T16:13:26.621455680Z",
#     "message": "3"
#   },
#   {
#     "time": "2024-08-05T16:13:16.587080625Z",
#     "message": "J"
#   }
# ]


class NewsResponse(BaseModel):
    time: datetime.datetime
    message: str

    def to_card(self) -> int:
        match self.message:
            case "A":
                return 1
            case "J":
                return 11
            case "Q":
                return 12
            case "K":
                return 13
            case _:
                return int(self.message)


NewsResponseList = RootModel[List[NewsResponse]]


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


class PositionResponse(BaseModel):
    product: str
    volume: int
    averageBuyPrice: float
    averageSellPrice: float


PositionResponseList = RootModel[List[PositionResponse]]


class PriceVolume:
    """
    Bundles a price and a volume

    Attributes
    ----------
    price: float

    volume: int
    """

    def __init__(self, price, volume):
        self.price = price
        self.volume = volume

    def __repr__(self):
        return f"PriceVolume(price={str(self.price)}, volume={str(self.volume)})"

    def __eq__(self, other):
        if not isinstance(other, PriceVolume):
            return NotImplemented
        return self.price == other.price and self.volume == other.volume

    # Used for formatting
    @property
    def price_width(self):
        return len(
            str(round(self.price, 3))
        )  # Currently limit price granularity to 3 d.p.

    @property
    def volume_width(self):
        return len(str(self.volume))


class PriceBook:
    """
    An order book at a specific point in time.

    Attributes
    ----------
    timestamp: datetime.datetime
        The time of the snapshot.

    instrument_id: str
        The id of the instrument the book is on.

    bids: List[PriceVolume]
        List of price points and volumes representing all bid orders.
        Sorted from highest price to lowest price (i.e. from best to worst).

    asks: List[PriceVolume]
        List of price points and volumes representing all ask orders.
        Sorted from lowest price to highest price (i.e. from best to worst).
    """

    def __init__(self, *, timestamp=None, instrument_id=None, bids=None, asks=None):
        self.timestamp: datetime = datetime(1970, 1, 1) if not timestamp else timestamp
        self.instrument_id: str = "" if not instrument_id else instrument_id
        self.bids: List[PriceVolume] = [] if not bids else bids
        self.asks: List[PriceVolume] = [] if not asks else asks

    def __repr__(self):
        book_desc = f"PriceBook({self.instrument_id} {self.timestamp})"
        book_header = ["#bids", "price", "#asks"]

        bid_width = (
                max([bid.volume_width for bid in self.bids] + [len(book_header[0])]) + 2
        )
        ask_width = (
                max([ask.volume_width for ask in self.asks] + [len(book_header[2])]) + 2
        )
        price_width = (
                max(
                    [order.price_width for order in self.asks + self.bids]
                    + [len(book_header[1])]
                )
                + 2
        )

        book_repr = [
            book_desc,
            self._format_level(book_header, bid_width, price_width, ask_width),
        ]
        for ask in self.asks[::-1]:
            ask_level = ["", str(round(ask.price, 3)), str(ask.volume)]
            ask_level = self._format_level(ask_level, bid_width, price_width, ask_width)
            book_repr.append(ask_level)
        for bid in self.bids:
            bid_level = [str(bid.volume), str(round(bid.price, 3)), ""]
            bid_level = self._format_level(bid_level, bid_width, price_width, ask_width)
            book_repr.append(bid_level)
        return "\n".join(book_repr)

    def __eq__(self, other):
        if not isinstance(other, PriceBook):
            return NotImplemented
        return (
                self.instrument_id == other.instrument_id
                and self.bids == other.bids
                and self.asks == other.asks
        )

    @staticmethod
    def _format_level(
            level: List[str], bid_width: int, price_width: int, ask_width: int
    ):
        assert (
                len(level) == 3
        ), "_format_level expects 3 elements in level (#bid, price, #ask)"
        return f"{level[0].center(bid_width, ' ')}|{level[1].center(price_width, ' ')}|{level[2].center(ask_width, ' ')}"


class OrderStatus:
    """
    Summary of an order.

    Attributes
    ----------
    order_id: int
        The id of the order.

    instrument_id: str
        The id of the traded instrument.

    price: float
        The price at which the instrument traded.

    volume: int
        The volume that was traded.

    side: 'bid' or 'ask'
        If 'bid' this is a bid order.
        If 'ask' this is an ask order.
    """

    def __init__(
            self, order_id: str, instrument_id: str, price: float, volume: int, side: Side
    ):
        self.order_id: str = order_id
        self.instrument_id: str = instrument_id
        self.price: float = price
        self.volume: int = volume
        self.side: Side = side

    def __repr__(self):
        return (
            f"OrderStatus(order_id={self.order_id}, instrument_id={self.instrument_id}, price={self.price}, "
            f"volume={self.volume}, side={self.side})"
        )
