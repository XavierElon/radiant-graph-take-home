import sys
import os
from datetime import datetime, timedelta, timezone
import random
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models import Base, Customer, Address, Order
from app.database import get_db

# Mock data
CITIES = {
    "CA": ["San Francisco", "Los Angeles", "San Diego"],
    "NY": ["New York", "Buffalo", "Albany"],
    "TX": ["Houston", "Dallas", "Austin"],
    "FL": ["Miami", "Orlando", "Tampa"]
}

ZIP_CODES = {
    "San Francisco": ["94105", "94107", "94110"],
    "Los Angeles": ["90001", "90002", "90003"],
    "San Diego": ["92101", "92102", "92103"],
    "New York": ["10001", "10002", "10003"],
    "Buffalo": ["14201", "14202", "14203"],
    "Albany": ["12201", "12202", "12203"],
    "Houston": ["77001", "77002", "77003"],
    "Dallas": ["75201", "75202", "75203"],
    "Austin": ["78701", "78702", "78703"],
    "Miami": ["33101", "33102", "33103"],
    "Orlando": ["32801", "32802", "32803"],
    "Tampa": ["33601", "33602", "33603"]
}

STREET_NAMES = [
    "Main St", "Market St", "Broadway", "Park Ave", "Lake Shore Dr",
    "Michigan Ave", "Pennsylvania Ave", "Peachtree St", "Bourbon St"
]

def create_mock_customer(session: Session, index: int) -> Customer:
    """Create a mock customer with random data."""
    first_names = ["John", "Jane", "Michael", "Emily", "David", "Sarah"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia"]
    
    customer = Customer(
        first_name=random.choice(first_names),
        last_name=random.choice(last_names),
        email=f"customer{index}@example.com",
        telephone=f"+1{random.randint(2000000000, 9999999999)}"
    )
    session.add(customer)
    session.commit()
    session.refresh(customer)
    return customer

def create_mock_address(session: Session, customer: Customer, is_billing: bool = False) -> Address:
    """Create a mock address for a customer."""
    state = random.choice(list(CITIES.keys()))
    city = random.choice(CITIES[state])
    zip_code = random.choice(ZIP_CODES[city])
    
    address = Address(
        street_address=f"{random.randint(1, 9999)} {random.choice(STREET_NAMES)}",
        apartment_suite=f"Apt {random.randint(1, 999)}" if random.random() > 0.5 else None,
        city=city,
        state=state,
        zip_code=zip_code,
        is_billing_address=is_billing,
        is_shipping_address=not is_billing,
        billing_customer_id=customer.id if is_billing else None,
        shipping_customer_id=customer.id if not is_billing else None
    )
    session.add(address)
    session.commit()
    session.refresh(address)
    return address

def create_mock_order(session: Session, customer: Customer, billing_address: Address, shipping_address: Address) -> Order:
    """Create a mock order with random data."""
    # Generate a random date within the last 30 days
    days_ago = random.randint(0, 30)
    hours_ago = random.randint(0, 23)
    minutes_ago = random.randint(0, 59)
    order_date = datetime.now(timezone.utc) - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)
    
    order = Order(
        customer_id=customer.id,
        order_date=order_date,
        total_amount=round(random.uniform(10.0, 1000.0), 2),
        status=random.choice(["completed", "pending", "cancelled"]),
        billing_address_id=billing_address.id,
        shipping_address_id=shipping_address.id
    )
    session.add(order)
    session.commit()
    session.refresh(order)
    return order

def create_mock_data():
    """Create mock data for testing."""
    # Get database session
    session = next(get_db())
    
    try:
        # Create 50 customers
        for i in range(50):
            # Create customer
            customer = create_mock_customer(session, i)
            
            # Create billing and shipping addresses
            billing_address = create_mock_address(session, customer, is_billing=True)
            shipping_address = create_mock_address(session, customer, is_billing=False)
            
            # Create 1-5 orders for each customer
            num_orders = random.randint(1, 5)
            for _ in range(num_orders):
                create_mock_order(session, customer, billing_address, shipping_address)
            
            print(f"Created customer {i+1}/50 with {num_orders} orders")
        
        print("Mock data creation completed successfully!")
        
    except Exception as e:
        print(f"Error creating mock data: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    create_mock_data() 