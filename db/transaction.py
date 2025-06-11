from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Float, Integer, String, DateTime
Base = declarative_base()

# SQLAlchemy Model
class TransactionDB(Base):
    __tablename__ = 'transactions'

    id = Column(String, primarykey=True, index=True)
    user_id = Column(Integer)
    amount = Column(Float)
    currency = Column(String)
    category = Column(String)
    timestamp = Column(DateTime)
