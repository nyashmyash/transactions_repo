import os
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import  create_engine, cast
from sqlalchemy.orm import sessionmaker, Session
from db.transaction import TransactionDB
from models.transaction import Transaction
from db.base import Base
from utils import  load_users, load_transactions_from_json, get_user_stats_db
# Database Configuration
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://user:password@localhost:5432/dbname") #Default URL, override by environment variable

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


users_data = [
    {
        'username': 'Dima',
        'weekly_limit' : -1000,
        'daily_limit' : -100,
    },
    {
        'username': 'Vasya',
        'weekly_limit': -1200,
        'daily_limit': -130,
    }
]

# Dependency Injection
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# FastAPI Endpoints
app = FastAPI()

@app.post("/transactions/")
async def create_transaction(transaction: Transaction, db: Session = Depends(get_db)):
    db_transaction = TransactionDB(transaction.model_dump())
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

@app.get("/transactions/{transaction_id}", response_model=Transaction)
async def read_transaction(transaction_id: str, db: Session = Depends(get_db)):
    transaction = db.query(TransactionDB).filter(TransactionDB.id == transaction_id).first()
    if transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction

@app.get("/load_users")
async def load_data(db: Session = Depends(get_db)):
    Base.metadata.create_all(bind=engine)
    loaded_users= load_users(users_data, db)
    return {"message": "Data users loaded successfully", "number of users": len(loaded_users)}


@app.get("/load_data")
async def load_data(db: Session = Depends(get_db)):
    loaded_transactions = load_transactions_from_json("data.json", db)
    return {"message": "Data loaded successfully", "number of records": len(loaded_transactions)}


from pydantic import BaseModel
from typing import Dict, Optional
from datetime import date

class UserStatsResponse(BaseModel):
    total_spent: float
    by_category: Dict[str, float]
    daily_average: float

@app.get("/users/{user_id}/stats", response_model=UserStatsResponse)
async def get_user_stats(user_id: int, from_date: Optional[date] = None, to_date: Optional[date] = None, db: Session = Depends(get_db)):
    ret = get_user_stats_db(db, user_id, from_date, to_date)
    return UserStatsResponse(**ret)


