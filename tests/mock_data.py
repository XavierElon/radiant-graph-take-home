"""Mock data for customer tests."""

# Base customer data
BASE_CUSTOMER = {
    "email": "test@example.com",
    "telephone": "+11234567890",  # 10 digits after +1
    "first_name": "John",
    "last_name": "Doe"
}

# Base address data
BASE_ADDRESS = {
    "street_address": "123 Test St",
    "apartment_suite": None,
    "city": "Test City",
    "state": "TS",
    "zip_code": "12345",
    "is_billing_address": False,
    "is_shipping_address": True
}

# Base order data
BASE_ORDER = {
    "total_amount": 100.0,
    "status": "completed",
    "order_type": "in_store"
}

def get_test_customers(count=3):
    """Generate a list of test customers."""
    return [
        {
            "email": f"test{i}@example.com",
            "telephone": f"+1123456789{i}",  # 10 digits after +1
            "first_name": f"John{i}",
            "last_name": f"Doe{i}"
        }
        for i in range(count)
    ]

def get_test_addresses(count=2):
    """Generate a list of test addresses."""
    return [
        {
            "street_address": f"123 Test St {i}",
            "apartment_suite": None,
            "city": "Test City",
            "state": "TS",
            "zip_code": "12345",
            "is_billing_address": False,
            "is_shipping_address": True
        }
        for i in range(count)
    ]

def get_test_addresses_with_zip_codes(zip_codes):
    """Generate a list of test addresses with specified zip codes."""
    return [
        {
            "street_address": "123 Test St",
            "apartment_suite": None,
            "city": "Test City",
            "state": "TS",
            "zip_code": zip_code,
            "is_billing_address": True,
            "is_shipping_address": True
        }
        for zip_code in zip_codes
    ]

def create_order_data(billing_address_id, shipping_address_ids, order_time):
    """Create order data with the given parameters.
    
    Args:
        billing_address_id: ID of the billing address
        shipping_address_ids: List of shipping address IDs with their sequence
        order_time: Time when the order was placed
    """
    return {
        **BASE_ORDER,
        "billing_address_id": billing_address_id,
        "shipping_addresses": [
            {"address_id": addr_id, "sequence": idx}
            for idx, addr_id in enumerate(shipping_address_ids, 1)
        ],
        "order_date": order_time.isoformat()
    } 