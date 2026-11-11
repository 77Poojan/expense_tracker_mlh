# Expense Tracker API

A small FastAPI expense tracker backed by SQLite.

## Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

The API is available at `http://127.0.0.1:8000`; interactive documentation is at
`http://127.0.0.1:8000/docs`. Data is stored in `expenses.db` by default. Set
`EXPENSES_DB` to use a different SQLite file.

## Endpoints

- `POST /expenses` — create an expense
- `GET /expenses` — list expenses
- `GET /expenses/{id}` — retrieve one expense
- `PUT /expenses/{id}` — replace an expense
- `DELETE /expenses/{id}` — delete an expense

Expense fields are `description`, positive `amount`, `category`, and optional
`date` (defaults to today, formatted as `YYYY-MM-DD`).~~