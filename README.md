# radiant-graph-take-home

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
cat > requirements.txt << 'EOF'
fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
python-dotenv==1.0.0
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.2
pydantic==2.5.0
email-validator==2.1.0
EOF

# Install all dependencies
pip install -r requirements.txt
```

### 5. Set Up Environment Variables

```bash
# Create environment file
cat > .env << 'EOF'
DATABASE_URL=postgresql://username:password@localhost/radiant_graph
EOF
```

username and password will come from the docker-compose.yml file

### 6. Run the Application via Tilt

Tilt was used to make it very easy to build the application in Docker containers with a nice GUI.

To install Tilt:

```
curl -fsSL https://raw.githubusercontent.com/tilt-dev/tilt/master/scripts/install.sh | bash
```

Once tilt is install run the command:

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

```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Install new package
pip install package-name

# Update requirements.txt
pip freeze > requirements.txt
```

### Stopping Work

```bash
# Stop the server with Ctrl+C, then deactivate virtual environment
deactivate
```

## Database Setup Options

### PostgreSQL

**Install PostgreSQL:**

```bash
# Using Homebrew
brew install postgresql

# Start PostgreSQL service
brew services start postgresql
```

**Update .env file:**

```bash
DATABASE_URL=postgresql://your_username:your_password@localhost/order_management
```

## Testing

```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Run tests
pytest tests/ -v

# Run tests with coverage
pip install pytest-cov
pytest tests/ --cov=app --cov-report=html

# View coverage report
open htmlcov/index.html
```

## Example API Usage

### Test the API

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

## Development Tips

### Using VS Code on macOS

```bash
# Install VS Code if you haven't
brew install --cask visual-studio-code

# Open project in VS Code
code .

# Install Python extension in VS Code
# Then select the Python interpreter from your venv:
# Cmd+Shift+P → "Python: Select Interpreter" → choose ./venv/bin/python
```

### Environment Variables for Different Stages

```bash
# Development
cp .env .env.development

# Production
cp .env .env.production
# Edit .env.production with production database settings
```

### Load Mock Data

```
python scripts/create_mock_data.py
```

### Curl commands to test API:

If you don't want to use an API tester programmer like Postman or Insomnia you can use the following curl commands:

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

## TESTING

Create testing database

```
psql -h localhost -p 5433 -U radiant -d postgres -c "CREATE DATABASE radiant_graph_test;"
```

password: radiant123

```
DATABASE_URL=postgresql://radiant:radiant123@localhost:5433/radiant_graph_test pytest -v
```
