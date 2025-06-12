from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Float, Integer, String, DateTime
from db.base import Base

class TransactionDB(Base):
    __tablename__ = 'transactions'

    id = Column(String, primary_key=True, index=True)
    user_id = Column(Integer)
    amount = Column(Float)
    currency = Column(String)
    category = Column(String)
    timestamp = Column(DateTime)

