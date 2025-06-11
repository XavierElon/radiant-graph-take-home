from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Annotated, Dict
from datetime import datetime

class AddressBase(BaseModel):
    """Base Pydantic model for address data.
    
    This model defines the common fields required for address creation and validation.
    """
    street_address: str
    apartment_suite: Optional[str] = None
    city: str  # City name
    state: Annotated[str, Field(min_length=2, max_length=2)]  # 2-letter state code
    zip_code: Annotated[str, Field(pattern=r'^\d{5}(-\d{4})?$')]  # Format: 12345 or 12345-6789
    is_billing_address: bool = False 
    is_shipping_address: bool = True  

class AddressCreate(AddressBase):
    """Pydantic model for creating a new address."""
    pass

class Address(AddressBase):
    """Pydantic model for address data including database fields."""
    id: int  # Database ID
    billing_customer_id: Optional[int] = None  # ID of customer using this as billing address
    shipping_customer_id: Optional[int] = None  # ID of customer using this as shipping address

    class Config:
        orm_mode = True

class CustomerBase(BaseModel):
    """Base Pydantic model for customer data.
    
    This model defines the common fields required for customer creation and validation.
    """
    first_name: str  
    last_name: str  
    email: EmailStr
    telephone: Annotated[str, Field(pattern=r'^\+?1?\d{10,15}$')]  # Validated phone number

class CustomerCreate(CustomerBase):
    """Pydantic model for creating a new customer."""
    pass

class OrderBase(BaseModel):
    """Base Pydantic model for order data.
    
    This model defines the common fields required for order creation and validation.
    """
    total_amount: float  
    status: str  # Order status (e.g., "pending", "completed", "cancelled")
    billing_address_id: int  
    shipping_address_id: int 
    order_type: str  # "in_store" or "online"

class OrderCreate(OrderBase):
    """Pydantic model for creating a new order."""
    pass

class Order(OrderBase):
    """Pydantic model for order data including database fields and relationships."""
    id: int  # Database ID
    customer_id: int  # ID of customer who placed the order
    order_date: datetime  # When the order was placed
    billing_address: Address  # Billing address details
    shipping_address: Address  # Shipping address details

    class Config:
        orm_mode = True

class Customer(CustomerBase):
    """Pydantic model for customer data including database fields and relationships."""
    id: int  # Database ID
    billing_addresses: List[Address] = []  # List of billing addresses
    shipping_addresses: List[Address] = []  # List of shipping addresses
    orders: List[Order] = []  # List of customer's orders

    class Config:
        orm_mode = True

class ZipCodeAnalytics(BaseModel):
    """Pydantic model for zip code-based order analytics."""
    zip_code: str  # Zip code being analyzed
    order_count: int  # Number of orders in this zip code

class TimeOfDayAnalytics(BaseModel):
    """Pydantic model for time-of-day based order analytics."""
    hour: int  # Hour of day (0-23)
    order_count: int  # Number of orders in this hour

class DayOfWeekAnalytics(BaseModel):
    """Pydantic model for day-of-week based order analytics."""
    day_of_week: int  # Day of week (0 = Monday, 6 = Sunday)
    order_count: int  # Number of orders on this day

class TopInStoreCustomerAnalytics(BaseModel):
    """Pydantic model for top in-store customer analytics."""
    customer_id: int  # Customer's database ID
    first_name: str  # Customer's first name
    last_name: str  # Customer's last name
    email: str  # Customer's email
    in_store_order_count: int  # Number of in-store orders by this customer

    class Config:
        orm_mode = True 