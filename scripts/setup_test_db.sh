#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "Setting up test database..."

# Check if psql is installed
if ! command -v psql &> /dev/null; then
    echo -e "${RED}Error: psql is not installed. Please install PostgreSQL first.${NC}"
    exit 1
fi

# Create test database
echo "Creating test database..."
PGPASSWORD=radiant123 psql -h localhost -p 5433 -U radiant -d postgres -c "CREATE DATABASE radiant_graph_test;" 2>/dev/null

# Check if database creation was successful
if [ $? -eq 0 ]; then
    echo -e "${GREEN}Test database created successfully!${NC}"
else
    echo -e "${RED}Error: Failed to create test database.${NC}"
    echo "This might be because:"
    echo "1. The database already exists"
    echo "2. The PostgreSQL server is not running"
    echo "3. The user 'radiant' doesn't exist or has incorrect permissions"
    echo "4. The port 5433 is not accessible"
    exit 1
fi

echo -e "${GREEN}Test database setup complete!${NC}" 