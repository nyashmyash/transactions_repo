import datetime
from db.user import UserDB
from models.transaction import Transaction
from models.user import  User
from db.transaction import TransactionDB
from sqlalchemy.orm import  Session
from typing import List
import json
from datetime import date
from sqlalchemy import  func


def get_week_start_end_date(date_):
    weekday = date_.weekday()
    start_date = date_ - datetime.timedelta(days=weekday)
    end_date = start_date + datetime.timedelta(days=6)

    return start_date, end_date

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
        if abs(user.get(day_s, 0) + amount) > abs(user_db.daily_limit):
            print(f'for user {user_db.id} over limit in {day_s} amount {user.get(day_s, 0)+ amount - user_db.daily_limit}')
        if abs(user.get(week_s, 0) + amount) > abs(user_db.weekly_limit):
            print(f'for user {user_db.id} over limit in {week_s} amount {user.get(week_s, 0) + amount - user_db.weekly_limit}')

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


def get_user_stats_db(db: Session, user_id: int, start_date: date, end_date: date):
    # Получаем общие траты
    total_spent_query = db.query(func.sum(TransactionDB.amount)).filter(
        TransactionDB.user_id == user_id,
        TransactionDB.timestamp >= start_date,
        TransactionDB.timestamp <= end_date
    ).scalar()

    # Получаем траты по категориям
    by_category_query = db.query(
        TransactionDB.category,
        func.sum(TransactionDB.amount).label('total_amount')
    ).filter(
        TransactionDB.user_id == user_id,
        TransactionDB.timestamp >= start_date,
        TransactionDB.timestamp <= end_date
    ).group_by(TransactionDB.category).all()

    # Получаем средние траты в день
    total_days = (end_date - start_date).days + 1  # Включаем оба конца
    daily_average = total_spent_query / total_days if total_days > 0 else 0

    # Формируем результат
    by_category = {category: total_amount for category, total_amount in by_category_query}

    return {
        "total_spent": total_spent_query or 0,
        "by_category": by_category,
        "daily_average": daily_average
    }