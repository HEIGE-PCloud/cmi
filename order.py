from enum import Enum
from pydantic import BaseModel


class Side(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


# {"side": "BUY", "price": 1.4, "volume": 1, "product": "75 C"}
class Order(BaseModel):
    side: Side
    price: float
    volume: int
    product: str
    
