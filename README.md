# Address Book API

Simple address book API built with FastAPI and SQLite

## Setup & Running

1. Create and activate a virtual environment:

```bash
# macOS / Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the application:

```bash
uvicorn app.main:app --reload
```

The database (`addressbook.db`) will be created automatically on startup
Interactive Swagger documentation is available at http://127.0.0.1:8000/docs

## Running Tests

Run the test suite with:

```bash
python -m unittest discover tests
```

## Endpoints

- `POST /addresses` - Create a new address (validates coordinates and required fields)
- `GET /addresses` - List addresses (supports `skip` and `limit` query params)
- `GET /addresses/{id}` - Retrieve a specific address
- `PUT /addresses/{id}` - Update an address
- `DELETE /addresses/{id}` - Delete an address
- `GET /addresses/nearby` - Find addresses within `distance_km` of a given `latitude` and `longitude`
