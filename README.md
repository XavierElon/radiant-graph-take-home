# radiant-graph-take-home

This application was built using

## Structure of Application

The application follows a layered architecture pattern to maintain separation of concerns and improve maintainability:

```
app/
├── api/                    # API Layer
│   ├── routes/            # FastAPI route handlers
│   │   ├── customers.py   # Customer-related endpoints
│   │   ├── orders.py      # Order-related endpoints
│   │   └── analytics.py   # Analytics endpoints
│   └── services/          # Business Logic Layer
│       ├── customer.py    # Customer business logic
│       ├── order.py       # Order business logic
│       └── analytics.py   # Analytics business logic
├── db/                    # Database Layer
│   ├── queries/          # Database queries
│   │   ├── customer.py   # Customer queries
│   │   ├── order.py      # Order queries
│   │   └── analytics.py  # Analytics queries
│   └── database.py       # Database connection and setup
├── models.py             # SQLAlchemy models
└── schemas.py            # Pydantic schemas
```

### Layer Separation

1. **API Layer (routes/)**

   - Handles HTTP requests and responses
   - Input validation using Pydantic schemas
   - Route definitions and endpoint logic
   - No business logic, only request/response handling

2. **Service Layer (services/)**

   - Contains business logic and rules
   - Orchestrates operations across multiple queries
   - Handles complex operations and validations
   - Independent of HTTP/API concerns

3. **Database Layer (db/queries/)**
   - Handles all database operations
   - Contains SQL queries and database-specific logic
   - Manages database connections and transactions
   - Isolated from business logic and API concerns

### Benefits of This Structure

1. **Separation of Concerns**

   - Each layer has a specific responsibility
   - Changes in one layer don't affect others
   - Easier to maintain and test

2. **Testability**

   - Each layer can be tested independently
   - Business logic can be tested without HTTP/DB
   - Database operations can be tested in isolation

3. **Maintainability**

   - Clear organization makes code easier to navigate
   - New features can be added without affecting existing code
   - Dependencies flow in one direction (API → Services → DB)

4. **Scalability**
   - Each layer can be scaled independently
   - Business logic can be reused across different interfaces
   - Database operations can be optimized without affecting business logic

# Order Management System - macOS Setup Guide

## Prerequisites

- python3
- git
- venv
- docker
- tilt
- postgres

## Quick Start

### 1. Clone the Repository

```bash
# Clone the repository
git clone git@github.com:XavierElon/radiant-graph-take-home.git
cd radiant-graph-take-home
```

### 2. Create Virtual Environment

```bash
# Create virtual environment using Python's built-in venv module
python3 -m venv venv
```

### 3. Activate Virtual Environment

```bash
# Activate the virtual environment
source venv/bin/activate
```

### 4. Install Dependencies

```bash
# Create requirements.txt file
# cat > requirements.txt << 'EOF'
# fastapi==0.104.1
# uvicorn==0.24.0
# sqlalchemy==2.0.23
# psycopg2-binary==2.9.9
# python-dotenv==1.0.0
# pytest==7.4.3
# pytest-asyncio==0.21.1
# httpx==0.25.2
# pydantic==2.5.0
# email-validator==2.1.0
# EOF

# Install all dependencies
pip install -r requirements.txt
```

### 5. Set Up Environment Variables

```bash
# Copy environemnt variable from example env file
cp .env .env.example
```

username and password will come from the docker-compose.yml file

### 7. Load mock data

```
python scripts/create_mock_data.py
```

If you need to clear the mock data for some reason you can use

```
python scripts/clear_data.py
```

### 6. Run the Application via Tilt

Tilt was used to make it very easy to build the application in Docker containers with a nice GUI.

To install Tilt:

```

curl -fsSL https://raw.githubusercontent.com/tilt-dev/tilt/master/scripts/install.sh | bash

```

Once tilt is installed run the command and it will automatically build your postgres and api container.:

```

tilt up

```

If you need to take down your containers you can use the command:

```

tilt down

```

All of your containers will be visible in the Docker app or more conveniently at:
http://localhost:10350/overview

The API will be available at `http://localhost:8000`

- **API Documentation**: `http://localhost:8000/docs`
- **Alternative Documentation**: `http://localhost:8000/redoc`

## Daily Development Workflow

### Installing New Packages

Update requirements.txt

```

pip freeze > requirements.txt

```


### Testing

In order to run the tests you need to first create a test database
Create testing database:

```

scripts/.setup_test_db.sh

```
You can then run the tests with:

```

pytest tests/ -v

````


### Testing the API

It is recommended to use the Swagger UI at
http://localhost:8000/docs
or http://localhost:8000/redoc

If you prefer the terminal/curl you can you following curl commands:

```bash
# Test basic endpoint
curl http://localhost:8000/

# Create a test customer
curl -X POST "http://localhost:8000/api/customers/" \
  -H "Content-Type: application/json" \
  -d '{
    "telephone": "4155551234",
    "email": "test@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "addresses": [
      {
        "label": "Home",
        "street_address_1": "123 Market Street",
        "city": "San Francisco",
        "state": "CA",
        "zip_code": "94105",
        "is_billing_default": true
      }
    ]
  }'

# Look up the customer
curl "http://localhost:8000/api/customers/lookup?email=test@example.com"
````

Create a new customer:

```
curl -X POST http://localhost:8000/customers/ \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "telephone": "1234567890"
  }'
```

Get all customers:

```
curl http://localhost:8000/customers/
```

Get a specific customer (replace {id} with actual customer ID):

```
curl http://localhost:8000/customers/{id}
```

Add an address to a customer (replace {id} with actual customer ID):

```
curl -X POST http://localhost:8000/customers/{id}/addresses/ \
  -H "Content-Type: application/json" \
  -d '{
    "street_address": "123 Main St",
    "apartment_suite": "Apt 4B",
    "city": "New York",
    "state": "NY",
    "zip_code": "10001",
    "is_billing_address": true,
    "is_shipping_address": false
  }'
```

Get all addresses for a customer (replace {id} with actual customer ID):

```
curl http://localhost:8000/customers/{id}/addresses/
```

Search customers:

```
curl http://localhost:8000/customers/search/{name}
```

Health check:

```
curl http://localhost:8000/health
```

Create new order for a customer

```
curl -X POST "http://localhost:8000/orders/customers/1/orders/" \
  -H "Content-Type: application/json" \
  -d '{
    "total_amount": 99.99,
    "status": "completed",
    "billing_address_id": 1,
    "shipping_address_id": 2
  }'
```

Get all orders

```
curl "http://localhost:8000/orders/customers/1/orders/"
```

Get orders with pagination (skip first 10, limit to 5 results)

```
curl "http://localhost:8000/orders/customers/1/orders/?skip=10&limit=5"
```

### Search orders by customer email or phone:

Search by email

```
curl "http://localhost:8000/orders/search/?query=john.doe@example.com"
```

Search by phone

```
curl "http://localhost:8000/orders/search/?query=4155551234"
```

With pagination

```
curl "http://localhost:8000/orders/search/?query=john.doe@example.com&skip=0&limit=10"
```

Get a specific order by ID:

```
curl "http://localhost:8000/orders/1"
```

Get orders by zip code:

# Get billing zip codes (descending order)

```
curl "http://localhost:8000/analytics/orders/zip-code/"
```

# Get shipping zip codes (ascending order)

```
curl "http://localhost:8000/analytics/orders/zip-code/?address_type=shipping&order_by=asc"
```

Get orders by time of day:

# Get top 5 busiest hours

```
curl "http://localhost:8000/analytics/orders/time-of-day/?limit=5"
```

Get orders by day of week:

# Get all days ordered by count

```
curl "http://localhost:8000/analytics/orders/day-of-week/"
```

Get top in-store customers:

```
curl "http://localhost:8000/analytics/customers/top-in-store/"
```

Get top in-store customers with custom limit (e.g., 10):

```
curl "http://localhost:8000/analytics/customers/top-in-store/?limit=10"
```

## Troubleshooting

### Common Issues and Solutions

**1. `python3: command not found`**

```bash
# Check if Python is installed
which python3

# If not installed, use Homebrew
brew install python
```

**2. `pip: command not found` after activating venv**

```bash
# Make sure venv is activated
source venv/bin/activate

# Check pip location
which pip

# If still issues, try
python -m pip --version
```

**3. Permission denied errors**

```bash
# Don't use sudo with pip in virtual environments
# If you see permission errors, make sure venv is activated
source venv/bin/activate
```

**4. PostgreSQL connection issues**

```bash
# Check if PostgreSQL is running
brew services list | grep postgresql

# Start PostgreSQL if not running
brew services start postgresql

# Check connection
psql -d order_management -c "SELECT version();"
```

**5. Port 8000 already in use**

```bash
# Find what's using the port
lsof -i :8000

# Kill the process if needed
kill -9 PID_NUMBER

# Or run on different port
uvicorn app.main:app --host 0.0.0.0 --port 8001
```

### Virtual Environment Issues

**Recreate virtual environment:**

```bash
# Deactivate current environment
deactivate

# Remove old environment
rm -rf venv

# Create new environment
python3 -m venv venv

# Activate and reinstall packages
source venv/bin/activate
pip install -r requirements.txt
```

**Check virtual environment status:**

```bash
# Check if venv is activated (should show venv path)
which python

# Should show something like: /path/to/your/project/venv/bin/python
```
