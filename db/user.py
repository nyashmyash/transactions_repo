from sqlalchemy import  Column, Integer, String, Float, Date
from db.base import Base

class UserDB(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String)
    weekly_limit = Column(Float)
    daily_limit = Column(Float)