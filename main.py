import os
import sqlite3
from contextlib import asynccontextmanager
from datetime import date as Date
from pathlib import Path
from typing import Iterator

from fastapi import Depends, FastAPI, HTTPException, Response, status
from pydantic import BaseModel, Field


DATABASE_PATH = Path(
    os.getenv("EXPENSES_DB", Path(__file__).with_name("expenses.db"))
)


class ExpenseCreate(BaseModel):
    description: str = Field(min_length=1, max_length=200)
    amount: float = Field(gt=0)
    category: str = Field(min_length=1, max_length=100)
    date: Date = Field(default_factory=Date.today)


class Expense(ExpenseCreate):
    id: int


def get_db() -> Iterator[sqlite3.Connection]:
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    try:
        yield connection
    finally:
        connection.close()


def initialize_db() -> None:
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT NOT NULL,
                amount REAL NOT NULL CHECK (amount > 0),
                category TEXT NOT NULL,
                date TEXT NOT NULL
            )
            """
        )


@asynccontextmanager
async def lifespan(_: FastAPI):
    initialize_db()
    yield


app = FastAPI(title="Expense Tracker API", lifespan=lifespan)


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Expense Tracker API", "docs": "/docs"}


@app.post(
    "/expenses",
    response_model=Expense,
    status_code=status.HTTP_201_CREATED,
)
def create_expense(
    expense: ExpenseCreate,
    db: sqlite3.Connection = Depends(get_db),
) -> Expense:
    cursor = db.execute(
        "INSERT INTO expenses (description, amount, category, date) "
        "VALUES (?, ?, ?, ?)",
        (
            expense.description,
            expense.amount,
            expense.category,
            expense.date.isoformat(),
        ),
    )
    db.commit()
    return Expense(id=cursor.lastrowid, **expense.model_dump())


@app.get("/expenses", response_model=list[Expense])
def list_expenses(db: sqlite3.Connection = Depends(get_db)) -> list[Expense]:
    rows = db.execute("SELECT * FROM expenses ORDER BY date DESC, id DESC").fetchall()
    return [Expense(**dict(row)) for row in rows]


@app.get("/expenses/{expense_id}", response_model=Expense)
def get_expense(
    expense_id: int,
    db: sqlite3.Connection = Depends(get_db),
) -> Expense:
    row = db.execute(
        "SELECT * FROM expenses WHERE id = ?", (expense_id,)
    ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    return Expense(**dict(row))


@app.put("/expenses/{expense_id}", response_model=Expense)
def update_expense(
    expense_id: int,
    expense: ExpenseCreate,
    db: sqlite3.Connection = Depends(get_db),
) -> Expense:
    cursor = db.execute(
        "UPDATE expenses SET description = ?, amount = ?, category = ?, date = ? "
        "WHERE id = ?",
        (
            expense.description,
            expense.amount,
            expense.category,
            expense.date.isoformat(),
            expense_id,
        ),
    )
    db.commit()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Expense not found")
    return Expense(id=expense_id, **expense.model_dump())


@app.delete("/expenses/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(expense_id: int, db: sqlite3.Connection = Depends(get_db)) -> Response:
    cursor = db.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    db.commit()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Expense not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
