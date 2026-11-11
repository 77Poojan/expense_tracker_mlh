# Spendwise Expense Tracker

Spendwise is a lightweight expense tracking app built with FastAPI and SQLite. It includes a simple web dashboard for viewing spending trends and a REST API for managing expenses.

## Features

- Create, read, update, and delete expense entries
- Store data in SQLite with automatic table creation
- View a dashboard with monthly totals and category summaries
- Filter and inspect expense records through the REST API
- Use a lightweight frontend served directly from the FastAPI app

## Project structure

```text
.
├── main.py              # FastAPI app and database logic
├── requirements.txt     # Python dependencies
├── expenses.db         # SQLite database file (created automatically)
├── static/
│   └── index.html      # Expense dashboard frontend
├── README.md
└── .venv/              # Optional local virtual environment
```

## Requirements

- Python 3.10+
- pip

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run the app

```bash
uvicorn main:app --reload
```

Then open:

- Dashboard: http://127.0.0.1:8000
- API docs: http://127.0.0.1:8000/docs

## Configuration

By default, the app stores data in `expenses.db` in the project root. To use a different database file, set the `EXPENSES_DB` environment variable:

```bash
EXPENSES_DB=/path/to/your/database.db uvicorn main:app --reload
```

## API key

The app does not issue API keys or currently validate them on the server. The
dashboard asks for a key and sends it in the `X-API-Key` header, but the
backend currently ignores that header, so no key is needed to use the app and
the API is not protected by authentication.

If you need a random secret for your own use, generate one locally with:

```bash
openssl rand -hex 32
```

This value is not an active app credential unless API-key validation is added
to the backend. Do not expose this app to untrusted networks assuming the
dashboard key prompt provides protection.

## Expense model

Each expense contains:

- `description`: required text
- `amount`: required positive number
- `category`: required text
- `date`: optional date in `YYYY-MM-DD` format; defaults to today
- `id`: generated automatically by SQLite

## API endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| POST | `/expenses` | Create a new expense |
| GET | `/expenses` | List all expenses |
| GET | `/expenses/{id}` | Get a single expense |
| PUT | `/expenses/{id}` | Update an expense |
| DELETE | `/expenses/{id}` | Delete an expense |

Example request:

```bash
curl -X POST "http://127.0.0.1:8000/expenses" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Groceries",
    "amount": 42.5,
    "category": "Food",
    "date": "2026-11-11"
  }'
```

Example response:

```json
{
  "id": 1,
  "description": "Groceries",
  "amount": 42.5,
  "category": "Food",
  "date": "2026-11-11"
}
```

## Notes

- The app creates the SQLite table automatically on startup if it does not exist.
- The frontend is served from the `static/index.html` file and communicates with the FastAPI backend.
- The dashboard keeps the entered API key in page memory only; it is not persisted in local storage or the database.

## Troubleshooting

If the app cannot start:

- ensure your virtual environment is active
- confirm all dependencies are installed with `pip install -r requirements.txt`
- verify the database path is writable and the SQLite file can be created
