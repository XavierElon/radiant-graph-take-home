import pytest
from fastapi import status
from datetime import datetime, timedelta, timezone

def create_test_order(client, customer_id, address_id, order_time):
    order_data = {
        "billing_address_id": address_id,
        "shipping_address_id": address_id,
        "total_amount": 100.0,
        "status": "completed",
        "order_date": order_time.isoformat()
    }
    response = client.post(f"/orders/customers/{customer_id}/orders/", json=order_data)
    print(f"Order creation response: {response.json()}")  # Debug log
    return response

def test_get_orders_by_zip_code(client):
    # Create a customer
    customer_data = {
        "email": "test@example.com",
        "telephone": "+11234567890",  # Updated to match pattern
        "first_name": "John",
        "last_name": "Doe"
    }
    response = client.post("/customers/", json=customer_data)
    customer_id = response.json()["id"]
    
    # Create addresses with different zip codes
    zip_codes = ["12345", "54321", "67890"]
    addresses = []
    for zip_code in zip_codes:
        address_data = {
            "street_address": "123 Test St",
            "apartment_suite": None,
            "city": "Test City",
            "state": "TS",
            "zip_code": zip_code,
            "is_billing_address": True,
            "is_shipping_address": True
        }
        response = client.post(f"/customers/{customer_id}/addresses/", json=address_data)
        addresses.append(response.json())
    
    # Create orders for each address
    base_time = datetime.now(timezone.utc)
    for address in addresses:
        create_test_order(client, customer_id, address["id"], base_time)
    
    # Test default parameters
    response = client.get("/analytics/orders/zip-code/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) > 0
    assert all("zip_code" in item and "order_count" in item for item in data)
    
    # Test with address_type=shipping
    response = client.get("/analytics/orders/zip-code/?address_type=shipping")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) > 0
    
    # Test with order=asc
    response = client.get("/analytics/orders/zip-code/?order=asc")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) > 0
    assert all(data[i]["order_count"] <= data[i+1]["order_count"] for i in range(len(data)-1))

def test_get_orders_by_time_of_day(client):
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
    
    # Create an address
    address_data = {
        "street_address": "123 Test St",
        "apartment_suite": None,
        "city": "Test City",
        "state": "TS",
        "zip_code": "12345",
        "is_billing_address": True,
        "is_shipping_address": True
    }
    response = client.post(f"/customers/{customer_id}/addresses/", json=address_data)
    print(f"Address creation response: {response.status_code} - {response.json()}")  # Debug log
    address_id = response.json()["id"]
    
    # Create orders at different hours
    base_time = datetime.now(timezone.utc)
    for hour in range(24):
        order_time = base_time.replace(hour=hour, minute=0, second=0, microsecond=0)
        response = create_test_order(client, customer_id, address_id, order_time)
        print(f"Created order for hour {hour}: {response.status_code}")  # Debug log
    
    # Test getting orders by time of day with default limit (10)
    response = client.get("/analytics/orders/time-of-day")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 10  # Default limit is 10
    assert all("hour" in item and "order_count" in item for item in data)
    assert all(0 <= item["hour"] < 24 for item in data)
    assert all(item["order_count"] >= 0 for item in data)
    
    # Test getting orders by time of day with limit=24
    response = client.get("/analytics/orders/time-of-day/?limit=24")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 24  # Should have data for all 24 hours when limit=24
    assert all("hour" in item and "order_count" in item for item in data)
    assert all(0 <= item["hour"] < 24 for item in data)
    assert all(item["order_count"] >= 0 for item in data)

def test_get_orders_by_day_of_week(client):
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
    
    # Create an address
    address_data = {
        "street_address": "123 Test St",
        "apartment_suite": None,
        "city": "Test City",
        "state": "TS",
        "zip_code": "12345",
        "is_billing_address": True,
        "is_shipping_address": True
    }
    response = client.post(f"/customers/{customer_id}/addresses/", json=address_data)
    print(f"Address creation response: {response.status_code} - {response.json()}")  # Debug log
    address_id = response.json()["id"]
    
    # Create orders for each day of the week
    base_time = datetime.now(timezone.utc)
    for day in range(7):
        order_time = base_time.replace(hour=12, minute=0, second=0, microsecond=0) + timedelta(days=day)
        response = create_test_order(client, customer_id, address_id, order_time)
        print(f"Created order for day {day}: {response.status_code}")  # Debug log
    
    # Test getting orders by day of week
    response = client.get("/analytics/orders/day-of-week")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 7  # Should have data for all 7 days
    assert all("day_of_week" in item and "order_count" in item for item in data)
    assert all(0 <= item["day_of_week"] < 7 for item in data)
    assert all(item["order_count"] >= 0 for item in data)
