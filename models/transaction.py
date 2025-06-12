from pydantic import Field, constr
from pydantic import BaseModel
from datetime import datetime
from models.category import Category
class Transaction(BaseModel):
    id: constr(pattern=r'^tx[0-9]{4}$')
    user_id: int = Field(..., gt=0)
    amount: float = Field(..., le=0)
    currency: constr(min_length=3, max_length=3)
    category: Category
    timestamp: datetime