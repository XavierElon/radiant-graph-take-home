import pytest
from fastapi import status
from fastapi.testclient import TestClient
from datetime import datetime
from app.main import app
from tests.mock_data import (
    BASE_CUSTOMER,
    BASE_ADDRESS,
    create_order_data,
    get_test_customers,
    get_test_addresses
)

client = TestClient(app)

@pytest.fixture
def setup_customer_with_addresses(client, db):
    """Create a test customer with addresses and return their IDs."""
    # Create customer
    customer_response = client.post("/customers/", json=BASE_CUSTOMER)
    print(f"Customer creation response: {customer_response.status_code} - {customer_response.json()}")  # Debug log
    assert customer_response.status_code == status.HTTP_200_OK, f"Customer creation failed: {customer_response.json()}"
    customer_id = customer_response.json()["id"]
    
    # Create addresses
    addresses = get_test_addresses(2)
    address_ids = []
    for addr in addresses:
        addr["customer_id"] = customer_id
        response = client.post(f"/customers/{customer_id}/addresses/", json=addr)
        print(f"Address creation response: {response.status_code} - {response.json()}")  # Debug log
        assert response.status_code == status.HTTP_200_OK, f"Address creation failed: {response.json()}"
        address_ids.append(response.json()["id"])
    
    return customer_id, address_ids

def test_create_order_success(client, db, setup_customer_with_addresses):
    """Test successful order creation."""
    customer_id, address_ids = setup_customer_with_addresses
    billing_id = address_ids[0]
    shipping_ids = address_ids[1:]  # Use remaining addresses as shipping addresses
    
    order_data = create_order_data(
        billing_address_id=billing_id,
        shipping_address_ids=shipping_ids,
        order_time=datetime.now()
    )
    
    response = client.post(f"/orders/customers/{customer_id}/orders/", json=order_data)
    print(f"Order creation response: {response.status_code} - {response.json()}")  # Debug log
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["customer_id"] == customer_id
    assert data["billing_address_id"] == billing_id
    assert len(data["shipping_addresses"]) == len(shipping_ids)
    assert all(addr["sequence"] == idx + 1 for idx, addr in enumerate(data["shipping_addresses"]))
    assert float(data["total_amount"]) == order_data["total_amount"]

def test_create_order_invalid_customer(client, db):
    """Test order creation with invalid customer ID."""
    order_data = create_order_data(
        billing_address_id=1,
        shipping_address_ids=[1],
        order_time=datetime.now()
    )
    
    response = client.post("/orders/customers/999/orders/", json=order_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Customer not found"

def test_create_order_invalid_addresses(client, db, setup_customer_with_addresses):
    """Test order creation with invalid addresses."""
    customer_id, _ = setup_customer_with_addresses
    
    order_data = create_order_data(
        billing_address_id=999,  # Invalid address ID
        shipping_address_ids=[999],  # Invalid address ID
        order_time=datetime.now()
    )
    
    response = client.post(f"/orders/customers/{customer_id}/orders/", json=order_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Invalid billing address"

def test_get_customer_orders(client, db, setup_customer_with_addresses):
    """Test retrieving customer orders."""
    customer_id, address_ids = setup_customer_with_addresses
    billing_id = address_ids[0]
    shipping_ids = address_ids[1:]
    
    # Create multiple orders
    for _ in range(3):
        order_data = create_order_data(
            billing_address_id=billing_id,
            shipping_address_ids=shipping_ids,
            order_time=datetime.now()
        )
        response = client.post(f"/orders/customers/{customer_id}/orders/", json=order_data)
        print(f"Order creation response: {response.status_code} - {response.json()}")  # Debug log
        assert response.status_code == status.HTTP_200_OK
    
    response = client.get(f"/orders/customers/{customer_id}/orders/")
    print(f"Get orders response: {response.status_code} - {response.json()}")  # Debug log
    assert response.status_code == status.HTTP_200_OK
    orders = response.json()
    assert len(orders) == 3
    assert all(order["customer_id"] == customer_id for order in orders)
    assert all(len(order["shipping_addresses"]) == len(shipping_ids) for order in orders)

def test_search_orders(client, db, setup_customer_with_addresses):
    """Test searching orders by email or phone."""
    customer_id, address_ids = setup_customer_with_addresses
    billing_id = address_ids[0]
    shipping_ids = address_ids[1:]
    
    # Create an order
    order_data = create_order_data(
        billing_address_id=billing_id,
        shipping_address_ids=shipping_ids,
        order_time=datetime.now()
    )
    response = client.post(f"/orders/customers/{customer_id}/orders/", json=order_data)
    print(f"Order creation response: {response.status_code} - {response.json()}")  # Debug log
    assert response.status_code == status.HTTP_200_OK
    
    # Search by email
    response = client.get(f"/orders/search/?query={BASE_CUSTOMER['email']}")
    print(f"Search by email response: {response.status_code} - {response.json()}")  # Debug log
    assert response.status_code == status.HTTP_200_OK
    orders = response.json()
    assert len(orders) > 0
    assert all(order["customer_id"] == customer_id for order in orders)
    
    # Search by phone
    response = client.get(f"/orders/search/?query={BASE_CUSTOMER['telephone']}")
    print(f"Search by phone response: {response.status_code} - {response.json()}")  # Debug log
    assert response.status_code == status.HTTP_200_OK
    orders = response.json()
    assert len(orders) > 0
    assert all(order["customer_id"] == customer_id for order in orders)

def test_get_order_by_id(client, db, setup_customer_with_addresses):
    """Test retrieving a specific order by ID."""
    customer_id, address_ids = setup_customer_with_addresses
    billing_id = address_ids[0]
    shipping_ids = address_ids[1:]
    
    # Create an order
    order_data = create_order_data(
        billing_address_id=billing_id,
        shipping_address_ids=shipping_ids,
        order_time=datetime.now()
    )
    create_response = client.post(f"/orders/customers/{customer_id}/orders/", json=order_data)
    print(f"Order creation response: {create_response.status_code} - {create_response.json()}")  # Debug log
    assert create_response.status_code == status.HTTP_200_OK
    order_id = create_response.json()["id"]
    
    # Get the order
    response = client.get(f"/orders/{order_id}")
    print(f"Get order response: {response.status_code} - {response.json()}")  # Debug log
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == order_id
    assert data["customer_id"] == customer_id
    assert data["billing_address_id"] == billing_id
    assert len(data["shipping_addresses"]) == len(shipping_ids)
    assert all(addr["sequence"] == idx + 1 for idx, addr in enumerate(data["shipping_addresses"]))

def test_get_nonexistent_order(client, db):
    """Test retrieving a non-existent order."""
    response = client.get("/orders/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Order not found"
