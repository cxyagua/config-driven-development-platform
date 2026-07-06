# Config-Driven Development Platform Server

FastAPI backend server for the Config-Driven Development Platform.

## Requirements

- Python 3.10+
- Poetry or pip

## Installation

### Using Poetry

```bash
poetry install
```

### Using pip

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Running the Server

### Development Mode

```bash
lsof -ti:8000 | xargs kill -9
cd server
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
cd server
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## API Documentation

Once the server is running, you can access:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
server/
├── app/
│   ├── api/
│   │   ├── endpoints/
│   │   │   └── health.py
│   │   ├── router.py
│   │   └── __init__.py
│   ├── core/
│   │   ├── config.py
│   │   └── __init__.py
│   ├── schemas/
│   │   └── __init__.py
│   ├── services/
│   │   └── __init__.py
│   ├── main.py
│   └── __init__.py
├── .env.example
├── .gitignore
├── pyproject.toml
├── requirements.txt
└── README.md
```

## Configuration

Copy `.env.example` to `.env` and fill in the values:

```bash
cp .env.example .env
```

### Environment Variables

- `APP_NAME`: Application name
- `APP_VERSION`: Application version
- `DEBUG`: Debug mode (true/false)
- `DATABASE_URL`: Database connection URL (leave empty for now)