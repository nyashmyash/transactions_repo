from sqlalchemy import create_engine, Column, Integer, String, Float, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import date

Base = declarative_base()

class UserDB(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String)
    weekly_limit = Column(Float)
    daily_limit = Column(Float)

    def __init__(self, username, weekly_limit, daily_limit):
        self.username = username
        self.weekly_limit = weekly_limit
        self.daily_limit = daily_limit


    # def check_limit(self, amount, session):
    #     today = date.today()
    #
    #     # Reset spending if it's a new day
    #     if self.last_reset_date != today:
    #         self.reset_daily_spending(session)
    #
    #     # Check limits
    #     if self.current_daily_spending + amount > self.daily_limit:
    #         print("Daily limit exceeded.")
    #         return False
    #
    #     if self.current_weekly_spending + amount > self.weekly_limit:
    #         print("Weekly limit exceeded.")
    #         return False
    #
    #     return True
    #
    # def record_transaction(self, amount, session):
    #     if self.check_limit(amount, session):
    #         self.current_weekly_spending += amount
    #         self.current_daily_spending += amount
    #         session.commit()
    #         print(f"Transaction of {amount} recorded. Remaining weekly: {self.weekly_limit - self.current_weekly_spending}, Daily: {self.daily_limit - self.current_daily_spending}")
    #         return True
    #     else:
    #         return False
    #
    # def reset_daily_spending(self, session):
    #     self.current_daily_spending = 0.0
    #     self.last_reset_date = date.today()
    #     session.commit()
    #     print("Daily spending reset.")