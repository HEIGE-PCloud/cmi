from enum import Enum
from typing import List
from pydantic import BaseModel, RootModel


class Side(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


# {"side": "BUY", "price": 1.4, "volume": 1, "product": "75 C"}
class Order(BaseModel):
    side: Side
    price: float
    volume: int
    product: str


OrderList = RootModel[List[Order]]
