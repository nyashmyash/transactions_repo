from pydantic import Field, constr
from pydantic import BaseModel
class User(BaseModel):
    username: constr(min_length=3, max_length=100)
    weekly_limit: float = Field(..., le=0)
    daily_limit: float = Field(..., le=0)