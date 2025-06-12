import json
import os
from typing import List
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import  create_engine, cast
from sqlalchemy.orm import sessionmaker, Session
from db.transaction import TransactionDB
from db.user import UserDB
from models.transaction import Transaction
from models.user import  User
from db.base import Base
from utils import get_week_start_end_date
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


def check_limits(transaction: TransactionDB, user_limits, db: Session):
    user_db = db.query(UserDB).filter(UserDB.id == transaction.user_id).first()
    amount = transaction.amount
    timestamp = transaction.timestamp
    day_s = f"day {timestamp.strftime('%d %b %Y')}"
    start, end = get_week_start_end_date(timestamp)
    week_s = f"week {start.strftime('%d %b %Y')}"

    if user_db:
        if user_db.id not in user_limits:
            user_limits[user_db.id] = {day_s: amount , week_s: amount}
        user = user_limits[user_db.id]
        if abs(user[day_s] + amount) > abs(user_db.daily_limit):
            print(f'for user {user_db.id} over limit in {day_s} amount {user[day_s] + amount - user_db.daily_limit}')
        if abs(user[week_s] + amount) > abs(user_db.weekly_limit):
            print(f'for user {user_db.id} over limit in {week_s} amount {user[week_s] + amount - user_db.weekly_limit}')

        user[day_s] = user.get(day_s, 0) + amount
        user[week_s] = user.get(week_s, 0) + amount
    else:
        print('User not found')


def load_users(data: list, db) -> List[User]:
    users = []
    for item in data:
        try:
            user = User(**item)
            db_user = UserDB(**user.model_dump())
            db.add(db_user)
            users.append(user)
        except ValueError as e:
            print(f"Validation error for item: {item}. Error: {e}")
            pass
    db.commit()
    return users


def load_transactions_from_json(filename: str, db: Session) -> List[Transaction]:
    transactions = []
    with open(filename, 'r') as f:
        data = json.load(f)

    user_limits = {}

    if isinstance(data, list):
        for item in data:
            try:
                transaction = Transaction(**item)
                db_transaction = TransactionDB(**transaction.model_dump())
                check_limits(db_transaction, user_limits, db)
                db.add(db_transaction)
                transactions.append(transaction)
            except ValueError as e:
                print(f"Validation error for item: {item}. Error: {e}")
                pass
    else:
        try:
            transaction = Transaction(**data)
            db_transaction = TransactionDB(**transaction.model_dump())
            check_limits(db_transaction, user_limits, db)
            db.add(db_transaction)
            transactions.append(transaction)
        except ValueError as e:
            print(f"Validation error for item: {data}. Error: {e}")
            pass

    db.commit()
    return transactions

@app.get("/load_users")
async def load_data(db: Session = Depends(get_db)):
    Base.metadata.create_all(bind=engine)
    loaded_users= load_users(users_data, db)
    return {"message": "Data users loaded successfully", "number of users": len(loaded_users)}


@app.get("/load_data")
async def load_data(db: Session = Depends(get_db)):
    loaded_transactions = load_transactions_from_json("data.json", db)
    return {"message": "Data loaded successfully", "number of records": len(loaded_transactions)}

