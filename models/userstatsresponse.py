from pydantic import BaseModel
from typing import Dict

class UserStatsResponse(BaseModel):
    total_spent: float
    by_category: Dict[str, float]
    daily_average: float