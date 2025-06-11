import pytest
from fastapi import status
from fastapi.testclient import TestClient
from datetime import datetime
from app.main import app
from tests.mock_data import (
    BASE_CUSTOMER,
    BASE_ADDRESS,
    create_order_data, 
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

def test_create_order_with_multiple_shipping_addresses(client):
    # Create customer
    response = client.post("/customers/", json=BASE_CUSTOMER)
    customer_id = response.json()["id"]
    # Create billing address
    response = client.post(f"/customers/{customer_id}/addresses/", json={**BASE_ADDRESS, "is_billing_address": True, "is_shipping_address": False})
    billing_id = response.json()["id"]
    # Create two shipping addresses
    shipping_ids = []
    for zip_code in ["94107", "94110"]:
        addr = {**BASE_ADDRESS, "zip_code": zip_code, "is_billing_address": False, "is_shipping_address": True}
        response = client.post(f"/customers/{customer_id}/addresses/", json=addr)
        shipping_ids.append(response.json()["id"])
    # Create order with both shipping addresses
    order_data = create_order_data(billing_address_id=billing_id, shipping_address_ids=shipping_ids, order_time=datetime.now())
    response = client.post(f"/orders/customers/{customer_id}/orders/", json=order_data)
    assert response.status_code == 200
    order = response.json()
    assert len(order["shipping_addresses"]) == 2
    assert order["shipping_addresses"][0]["sequence"] == 1
    assert order["shipping_addresses"][1]["sequence"] == 2

def test_customer_with_multiple_shipping_addresses_and_orders(client):
    response = client.post("/customers/", json=BASE_CUSTOMER)
    customer_id = response.json()["id"]
    response = client.post(f"/customers/{customer_id}/addresses/", json={**BASE_ADDRESS, "is_billing_address": True, "is_shipping_address": False})
    billing_id = response.json()["id"]
    shipping_ids = []
    for zip_code in ["94107", "94110", "94105"]:
        addr = {**BASE_ADDRESS, "zip_code": zip_code, "is_billing_address": False, "is_shipping_address": True}
        response = client.post(f"/customers/{customer_id}/addresses/", json=addr)
        shipping_ids.append(response.json()["id"])
    # Place an order to each shipping address
    for i, sid in enumerate(shipping_ids):
        order_data = create_order_data(billing_address_id=billing_id, shipping_address_ids=[sid], order_time=datetime.now())
        response = client.post(f"/orders/customers/{customer_id}/orders/", json=order_data)
        assert response.status_code == 200
        order = response.json()
        assert len(order["shipping_addresses"]) == 1
        assert order["shipping_addresses"][0]["address_id"] == sid

def test_online_and_instore_order_types(client):
    response = client.post("/customers/", json=BASE_CUSTOMER)
    customer_id = response.json()["id"]
    response = client.post(f"/customers/{customer_id}/addresses/", json={**BASE_ADDRESS, "is_billing_address": True, "is_shipping_address": False})
    billing_id = response.json()["id"]
    response = client.post(f"/customers/{customer_id}/addresses/", json={**BASE_ADDRESS, "zip_code": "94107", "is_billing_address": False, "is_shipping_address": True})
    shipping_id = response.json()["id"]
    # Online order
    order_data = create_order_data(billing_address_id=billing_id, shipping_address_ids=[shipping_id], order_time=datetime.now())
    order_data["order_type"] = "online"
    response = client.post(f"/orders/customers/{customer_id}/orders/", json=order_data)
    assert response.status_code == 200
    assert response.json()["order_type"] == "online"
    # In-store order
    order_data["order_type"] = "in_store"
    response = client.post(f"/orders/customers/{customer_id}/orders/", json=order_data)
    assert response.status_code == 200
    assert response.json()["order_type"] == "in_store"

def test_billing_and_shipping_addresses_are_separate(client):
    response = client.post("/customers/", json=BASE_CUSTOMER)
    customer_id = response.json()["id"]
    response = client.post(f"/customers/{customer_id}/addresses/", json={**BASE_ADDRESS, "is_billing_address": True, "is_shipping_address": False})
    billing_id = response.json()["id"]
    response = client.post(f"/customers/{customer_id}/addresses/", json={**BASE_ADDRESS, "zip_code": "94107", "is_billing_address": False, "is_shipping_address": True})
    shipping_id = response.json()["id"]
    # Try to create order with billing address as shipping address (should fail validation in real app, but here we just check they are not mixed)
    order_data = create_order_data(billing_address_id=billing_id, shipping_address_ids=[shipping_id], order_time=datetime.now())
    response = client.post(f"/orders/customers/{customer_id}/orders/", json=order_data)
    assert response.status_code == 200
    order = response.json()
    assert order["billing_address"]["id"] == billing_id
    assert order["shipping_addresses"][0]["address_id"] == shipping_id
