# Vehicle REST API

A simple REST API for managing vehicle records, built with FastAPI, SQLite, and Python.

## Features

- Full CRUD operations for Vehicle resources
- Case-insensitive VIN uniqueness constraint
- Comprehensive validation and error handling
- SQLite database for easy local development
- RESTful API design with proper HTTP status codes

## Project Structure

```
ApolloCodingExercise/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI application and routes
│   ├── models.py        # SQLAlchemy database models
│   ├── schemas.py       # Pydantic request/response schemas
│   └── database.py      # Database configuration
├── tests/
│   ├── __init__.py
│   └── test_vehicles.py # Test suite
├── pyproject.toml       # Poetry configuration
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Vehicle Model

A vehicle has the following attributes:

- `vin` (string, required, unique, case-insensitive): Vehicle Identification Number
- `manufacturer_name` (string, required): Manufacturer name
- `description` (string, optional): Vehicle description
- `horse_power` (integer, required, > 0): Horsepower
- `model_name` (string, required): Model name
- `model_year` (integer, required, 1900-2100): Model year
- `purchase_price` (float, required, > 0): Purchase price
- `fuel_type` (string, required): Fuel type

## API Endpoints

### GET /vehicle
List all vehicles.

**Response:** `200 OK`
```json
[
  {
    "vin": "1HGBH41JXMN109186",
    "manufacturer_name": "Honda",
    "description": "A reliable sedan",
    "horse_power": 180,
    "model_name": "Accord",
    "model_year": 2020,
    "purchase_price": 25000.0,
    "fuel_type": "Gasoline"
  }
]
```

### POST /vehicle
Create a new vehicle.

**Request Body:**
```json
{
  "vin": "1HGBH41JXMN109186",
  "manufacturer_name": "Honda",
  "description": "A reliable sedan",
  "horse_power": 180,
  "model_name": "Accord",
  "model_year": 2020,
  "purchase_price": 25000.00,
  "fuel_type": "Gasoline"
}
```

**Response:** `201 Created`
```json
{
  "vin": "1HGBH41JXMN109186",
  "manufacturer_name": "Honda",
  "description": "A reliable sedan",
  "horse_power": 180,
  "model_name": "Accord",
  "model_year": 2020,
  "purchase_price": 25000.0,
  "fuel_type": "Gasoline"
}
```

### GET /vehicle/{vin}
Get a vehicle by VIN (case-insensitive).

**Response:** `200 OK`
```json
{
  "vin": "1HGBH41JXMN109186",
  "manufacturer_name": "Honda",
  "description": "A reliable sedan",
  "horse_power": 180,
  "model_name": "Accord",
  "model_year": 2020,
  "purchase_price": 25000.0,
  "fuel_type": "Gasoline"
}
```

### PUT /vehicle/{vin}
Update a vehicle by VIN (case-insensitive). All fields are optional.

**Request Body:**
```json
{
  "horse_power": 200,
  "purchase_price": 27000.00
}
```

**Response:** `200 OK`
```json
{
  "vin": "1HGBH41JXMN109186",
  "manufacturer_name": "Honda",
  "description": "A reliable sedan",
  "horse_power": 200,
  "model_name": "Accord",
  "model_year": 2020,
  "purchase_price": 27000.0,
  "fuel_type": "Gasoline"
}
```

### DELETE /vehicle/{vin}
Delete a vehicle by VIN (case-insensitive).

**Response:** `204 No Content` (no response body)

## Error Responses

### 400 Bad Request
Returned when the request body cannot be parsed as JSON.

```json
{
  "detail": "Invalid JSON"
}
```

### 422 Unprocessable Entity
Returned when the request is valid JSON but fails validation.

```json
{
  "errors": {
    "horse_power": "Input should be greater than 0",
    "model_year": "Input should be greater than or equal to 1900"
  }
}
```

### 404 Not Found
Returned when a vehicle with the specified VIN is not found.

```json
{
  "detail": "Vehicle not found"
}
```

## Prerequisites

- Python 3.9 or higher
- Poetry (for dependency management)

## Installation

1. **Install Poetry** (if not already installed):
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. **Install dependencies**:
   ```bash
   poetry install
   ```

   Alternatively, if you prefer using pip:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up the database**:
   ```bash
   poetry run python setup_db.py
   ```
   
   This will create the `vehicles` database and all required tables.

## Running the Application

1. **Start the server**:
   ```bash
   poetry run uvicorn app.main:app --reload
   ```

   Or with pip:
   ```bash
   uvicorn app.main:app --reload
   ```

2. **Access the API**:
   - API: http://localhost:8000
   - Interactive API docs: http://localhost:8000/docs
   - Alternative API docs: http://localhost:8000/redoc

### Database Setup

The application uses PostgreSQL only. For local development, it automatically connects to:
`postgresql://postgres:postgres@localhost:5432/vehicles`

**Initial Setup:**

1. Make sure PostgreSQL is installed and running:
   ```bash
   # On macOS
   brew services start postgresql
   
   # On Linux
   sudo systemctl start postgresql
   ```

2. Run the database setup script to create the database and tables:
   ```bash
   poetry run python setup_db.py
   ```

3. If your PostgreSQL credentials are different, edit `app/database.py` and update `LOCAL_DB_URL`.

**Production/Remote Database:**

For production or remote databases, set the `DATABASE_URL` environment variable:
```bash
export DATABASE_URL="postgresql://user:password@host:5432/dbname"
poetry run uvicorn app.main:app --reload
```

**Important:** When using `DATABASE_URL` (production/remote), the application will **not** automatically create tables on startup. You must set up the database schema manually using migrations or the `setup_db.py` script (pointed at your production database).

For local development (no `DATABASE_URL` set), tables are automatically created on startup.

## Running Tests

Run the test suite using pytest:

```bash
poetry run pytest
```

Or with pip:
```bash
pytest
```

For verbose output:
```bash
poetry run pytest -v
```

## Example Usage

### Create a vehicle
```bash
curl -X POST "http://localhost:8000/vehicle" \
  -H "Content-Type: application/json" \
  -d '{
    "vin": "1HGBH41JXMN109186",
    "manufacturer_name": "Honda",
    "description": "A reliable sedan",
    "horse_power": 180,
    "model_name": "Accord",
    "model_year": 2020,
    "purchase_price": 25000.00,
    "fuel_type": "Gasoline"
  }'
```

### Get all vehicles
```bash
curl -X GET "http://localhost:8000/vehicle"
```

### Get a specific vehicle
```bash
curl -X GET "http://localhost:8000/vehicle/1HGBH41JXMN109186"
```

### Update a vehicle
```bash
curl -X PUT "http://localhost:8000/vehicle/1HGBH41JXMN109186" \
  -H "Content-Type: application/json" \
  -d '{
    "horse_power": 200,
    "purchase_price": 27000.00
  }'
```

### Delete a vehicle
```bash
curl -X DELETE "http://localhost:8000/vehicle/1HGBH41JXMN109186"
```

## Development

### Database

The application uses SQLite for simplicity. The database file (`vehicles.db`) is created automatically on first run. To reset the database, simply delete the `vehicles.db` file.

### Code Structure

- **app/main.py**: FastAPI application with route handlers
- **app/models.py**: SQLAlchemy ORM models
- **app/schemas.py**: Pydantic models for request/response validation
- **app/database.py**: Database connection and session management
- **tests/test_vehicles.py**: Comprehensive test suite

## Notes

- VINs are automatically normalized to uppercase for storage and lookup
- VIN uniqueness is enforced case-insensitively
- All numeric fields are validated (e.g., horse_power > 0, purchase_price > 0)
- Model year must be between 1900 and 2100

