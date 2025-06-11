from enum import Enum

class Category(str, Enum):
    food = "Food"
    transport = "Transport"
    entertainment = "Entertainment"
    utilities = "Utilities"
    other = "Other"