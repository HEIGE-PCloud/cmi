from enum import Enum
from typing import List, Optional
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
