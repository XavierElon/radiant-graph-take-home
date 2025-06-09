import pytest
from fastapi import status
from .mock_data import BASE_CUSTOMER, BASE_ADDRESS, get_test_customers, get_test_addresses

def test_create_customer(client):
    response = client.post("/customers/", json=BASE_CUSTOMER)
    print(f"Customer creation response: {response.status_code} - {response.json()}")  # Debug log
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == BASE_CUSTOMER["email"]
    assert data["telephone"] == BASE_CUSTOMER["telephone"]
    assert data["first_name"] == BASE_CUSTOMER["first_name"]
    assert data["last_name"] == BASE_CUSTOMER["last_name"]
    assert "id" in data

def test_create_duplicate_customer(client):
    # Create first customer
    response = client.post("/customers/", json=BASE_CUSTOMER)
    print(f"First customer creation response: {response.status_code} - {response.json()}")  # Debug log
    
    # Try to create duplicate customer
    response = client.post("/customers/", json=BASE_CUSTOMER)
    print(f"Duplicate customer creation response: {response.status_code} - {response.json()}")  # Debug log
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Email already registered" in response.json()["detail"]

def test_get_customers(client):
    # Create test customers
    customers = get_test_customers(3)
    
    for customer in customers:
        response = client.post("/customers/", json=customer)
        print(f"Customer creation response: {response.status_code} - {response.json()}")  # Debug log
    
    # Test getting all customers
    response = client.get("/customers/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 3

def test_get_customer_by_id(client):
    # Create a customer
    response = client.post("/customers/", json=BASE_CUSTOMER)
    print(f"Customer creation response: {response.status_code} - {response.json()}")  # Debug log
    customer_id = response.json()["id"]
    
    # Test getting customer by ID
    response = client.get(f"/customers/{customer_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == BASE_CUSTOMER["email"]
    assert data["id"] == customer_id

def test_get_nonexistent_customer(client):
    response = client.get("/customers/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Customer not found" in response.json()["detail"]

def test_create_customer_address(client):
    # Create a customer first
    response = client.post("/customers/", json=BASE_CUSTOMER)
    print(f"Customer creation response: {response.status_code} - {response.json()}")  # Debug log
    customer_id = response.json()["id"]
    
    # Create address for customer
    response = client.post(f"/customers/{customer_id}/addresses/", json=BASE_ADDRESS)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["street_address"] == BASE_ADDRESS["street_address"]
    assert data["city"] == BASE_ADDRESS["city"]
    assert "id" in data

def test_get_customer_addresses(client):
    # Create a customer
    response = client.post("/customers/", json=BASE_CUSTOMER)
    print(f"Customer creation response: {response.status_code} - {response.json()}")  # Debug log
    customer_id = response.json()["id"]
    
    # Create two addresses
    addresses = get_test_addresses(2)
    
    for address in addresses:
        client.post(f"/customers/{customer_id}/addresses/", json=address)
    
    # Test getting all addresses
    response = client.get(f"/customers/{customer_id}/addresses/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2

def test_search_customers(client):
    # Create test customers
    customers = get_test_customers(3)
    
    for customer in customers:
        response = client.post("/customers/", json=customer)
        print(f"Customer creation response: {response.status_code} - {response.json()}")  # Debug log
    
    # Test search
    response = client.get("/customers/search/John")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 3  # Should find all customers with "John" in their name
