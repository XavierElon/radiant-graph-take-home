import pytest
from fastapi import status
from datetime import datetime, timedelta, timezone
from .mock_data import (
    BASE_CUSTOMER, BASE_ADDRESS, BASE_ORDER,
    get_test_addresses_with_zip_codes,
    create_order_data,
    get_test_customers
)

@pytest.fixture
def setup_customer_with_addresses(client, db):
    """Create a test customer with addresses and return their IDs."""
    # Create customer
    customer_response = client.post("/customers/", json=BASE_CUSTOMER)
    assert customer_response.status_code == status.HTTP_200_OK
    customer_id = customer_response.json()["id"]
    
    # Create addresses
    addresses = get_test_addresses_with_zip_codes(["12345", "54321"])
    address_ids = []
    for addr in addresses:
        response = client.post(f"/customers/{customer_id}/addresses/", json=addr)
        assert response.status_code == status.HTTP_200_OK
        address_ids.append(response.json()["id"])
    
    return customer_id, address_ids

def create_test_order(client, customer_id, address_id, order_time):
    order_data = create_order_data(
        billing_address_id=address_id,
        shipping_address_ids=[address_id],
        order_time=order_time
    )
    response = client.post(f"/orders/customers/{customer_id}/orders/", json=order_data)
    print(f"Order creation response: {response.json()}")  # Debug log
    return response

def test_get_orders_by_zip_code(client):
    # Create a customer
    response = client.post("/customers/", json=BASE_CUSTOMER)
    customer_id = response.json()["id"]
    
    # Create addresses with different zip codes
    zip_codes = ["12345", "54321", "67890"]
    addresses = []
    for address_data in get_test_addresses_with_zip_codes(zip_codes):
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
    
    # Test with order=desc
    response = client.get("/analytics/orders/zip-code/?order=desc")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) > 0
    assert all(data[i]["order_count"] >= data[i+1]["order_count"] for i in range(len(data)-1))

def test_get_orders_by_time_of_day(client):
    # Create a customer
    response = client.post("/customers/", json=BASE_CUSTOMER)
    print(f"Customer creation response: {response.status_code} - {response.json()}")  # Debug log
    customer_id = response.json()["id"]
    
    # Create an address
    response = client.post(f"/customers/{customer_id}/addresses/", json=BASE_ADDRESS)
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
    response = client.post("/customers/", json=BASE_CUSTOMER)
    print(f"Customer creation response: {response.status_code} - {response.json()}")  # Debug log
    customer_id = response.json()["id"]
    
    # Create an address
    response = client.post(f"/customers/{customer_id}/addresses/", json=BASE_ADDRESS)
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

def test_get_top_in_store_customers(client, db):
    """Test getting top customers by in-store orders."""
    # Create multiple customers with different numbers of orders
    customers = get_test_customers(10)  # Create 10 test customers
    customer_orders = {}  # Track number of orders per customer
    
    for i, customer in enumerate(customers):
        # Create customer
        response = client.post("/customers/", json=customer)
        assert response.status_code == status.HTTP_200_OK
        customer_id = response.json()["id"]
        
        # Create address for the customer
        response = client.post(f"/customers/{customer_id}/addresses/", json=BASE_ADDRESS)
        assert response.status_code == status.HTTP_200_OK
        address_id = response.json()["id"]
        
        # Create different number of orders for each customer
        # Customer 0: 1 order, Customer 1: 2 orders, etc.
        num_orders = i + 1
        customer_orders[customer_id] = num_orders
        
        for _ in range(num_orders):
            order_data = create_order_data(
                billing_address_id=address_id,
                shipping_address_ids=[address_id],
                order_time=datetime.now()
            )
            order_data["order_type"] = "in_store"
            response = client.post(f"/orders/customers/{customer_id}/orders/", json=order_data)
            assert response.status_code == status.HTTP_200_OK
    
    # Test getting top in-store customers with default limit (5)
    response = client.get("/analytics/customers/top-in-store/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) <= 5  # Should return at most 5 customers
    
    # Verify the order counts are correct and in descending order
    for i in range(len(data) - 1):
        assert data[i]["in_store_order_count"] >= data[i + 1]["in_store_order_count"]
    
    # Verify the top customer has the most orders
    assert data[0]["in_store_order_count"] == 10  # Customer 9 should have 10 orders
    
    # Test with custom limit
    response = client.get("/analytics/customers/top-in-store/?limit=3")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 3
    assert data[0]["in_store_order_count"] == 10  # Top customer should have 10 orders
    assert data[1]["in_store_order_count"] == 9   # Second customer should have 9 orders
    assert data[2]["in_store_order_count"] == 8   # Third customer should have 8 orders

def test_get_in_store_orders_by_time_of_day(client):
    # Create a customer
    response = client.post("/customers/", json=BASE_CUSTOMER)
    customer_id = response.json()["id"]
    
    # Create an address
    response = client.post(f"/customers/{customer_id}/addresses/", json=BASE_ADDRESS)
    address_id = response.json()["id"]
    
    # Create in-store orders at different hours
    base_time = datetime.now(timezone.utc)
    for hour in range(24):
        order_time = base_time.replace(hour=hour, minute=0, second=0, microsecond=0)
        order_data = create_order_data(
            billing_address_id=address_id,
            shipping_address_ids=[address_id],
            order_time=order_time
        )
        order_data["order_type"] = "in_store"
        response = client.post(f"/orders/customers/{customer_id}/orders/", json=order_data)
        assert response.status_code == status.HTTP_200_OK
    
    # Test getting in-store orders by time of day
    response = client.get("/analytics/orders/time-of-day/?order_type=in_store")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) > 0
    assert all("hour" in item and "order_count" in item for item in data)
    assert all(0 <= item["hour"] < 24 for item in data)
    assert all(item["order_count"] >= 0 for item in data)
