import pytest
from fastapi import status

def test_create_customer(client):
    customer_data = {
        "email": "test@example.com",
        "telephone": "+11234567890",  # 10 digits after +1
        "first_name": "John",
        "last_name": "Doe"
    }
    response = client.post("/customers/", json=customer_data)
    print(f"Customer creation response: {response.status_code} - {response.json()}")  # Debug log
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == customer_data["email"]
    assert data["telephone"] == customer_data["telephone"]
    assert data["first_name"] == customer_data["first_name"]
    assert data["last_name"] == customer_data["last_name"]
    assert "id" in data

def test_create_duplicate_customer(client):
    # Create first customer
    customer_data = {
        "email": "test@example.com",
        "telephone": "+11234567890",  # 10 digits after +1
        "first_name": "John",
        "last_name": "Doe"
    }
    response = client.post("/customers/", json=customer_data)
    print(f"First customer creation response: {response.status_code} - {response.json()}")  # Debug log
    
    # Try to create duplicate customer
    response = client.post("/customers/", json=customer_data)
    print(f"Duplicate customer creation response: {response.status_code} - {response.json()}")  # Debug log
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Email already registered" in response.json()["detail"]

def test_get_customers(client):
    # Create test customers
    customers = [
        {
            "email": f"test{i}@example.com",
            "telephone": f"+1123456789{i}",  # 10 digits after +1
            "first_name": f"John{i}",
            "last_name": f"Doe{i}"
        }
        for i in range(3)
    ]
    
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
    customer_data = {
        "email": "test@example.com",
        "telephone": "+11234567890",  # 10 digits after +1
        "first_name": "John",
        "last_name": "Doe"
    }
    response = client.post("/customers/", json=customer_data)
    print(f"Customer creation response: {response.status_code} - {response.json()}")  # Debug log
    customer_id = response.json()["id"]
    
    # Test getting customer by ID
    response = client.get(f"/customers/{customer_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == customer_data["email"]
    assert data["id"] == customer_id

def test_get_nonexistent_customer(client):
    response = client.get("/customers/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Customer not found" in response.json()["detail"]

def test_create_customer_address(client):
    # Create a customer first
    customer_data = {
        "email": "test@example.com",
        "telephone": "+11234567890",  # 10 digits after +1
        "first_name": "John",
        "last_name": "Doe"
    }
    response = client.post("/customers/", json=customer_data)
    print(f"Customer creation response: {response.status_code} - {response.json()}")  # Debug log
    customer_id = response.json()["id"]
    
    # Create address for customer
    address_data = {
        "street_address": "123 Test St",
        "apartment_suite": None,
        "city": "Test City",
        "state": "TS",
        "zip_code": "12345",
        "is_billing_address": False,
        "is_shipping_address": True
    }
    response = client.post(f"/customers/{customer_id}/addresses/", json=address_data)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["street_address"] == address_data["street_address"]
    assert data["city"] == address_data["city"]
    assert "id" in data

def test_get_customer_addresses(client):
    # Create a customer
    customer_data = {
        "email": "test@example.com",
        "telephone": "+11234567890",  # 10 digits after +1
        "first_name": "John",
        "last_name": "Doe"
    }
    response = client.post("/customers/", json=customer_data)
    print(f"Customer creation response: {response.status_code} - {response.json()}")  # Debug log
    customer_id = response.json()["id"]
    
    # Create two addresses
    addresses = [
        {
            "street_address": f"123 Test St {i}",
            "apartment_suite": None,
            "city": "Test City",
            "state": "TS",
            "zip_code": "12345",
            "is_billing_address": False,
            "is_shipping_address": True
        }
        for i in range(2)
    ]
    
    for address in addresses:
        client.post(f"/customers/{customer_id}/addresses/", json=address)
    
    # Test getting all addresses
    response = client.get(f"/customers/{customer_id}/addresses/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2

def test_search_customers(client):
    # Create test customers
    customers = [
        {
            "email": f"test{i}@example.com",
            "telephone": f"+1123456789{i}",  # 10 digits after +1
            "first_name": f"John{i}",
            "last_name": f"Doe{i}"
        }
        for i in range(3)
    ]
    
    for customer in customers:
        response = client.post("/customers/", json=customer)
        print(f"Customer creation response: {response.status_code} - {response.json()}")  # Debug log
    
    # Test search
    response = client.get("/customers/search/John")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 3  # Should find all customers with "John" in their name
