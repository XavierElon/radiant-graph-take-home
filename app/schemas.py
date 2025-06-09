from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Annotated, Dict
from datetime import datetime

class AddressBase(BaseModel):
    street_address: str
    apartment_suite: Optional[str] = None
    city: str
    state: Annotated[str, Field(min_length=2, max_length=2)]  # 2-letter state code
    zip_code: Annotated[str, Field(pattern=r'^\d{5}(-\d{4})?$')] 
    is_billing_address: bool = False
    is_shipping_address: bool = True

class AddressCreate(AddressBase):
    pass

class Address(AddressBase):
    id: int
    billing_customer_id: Optional[int] = None
    shipping_customer_id: Optional[int] = None

    class Config:
        orm_mode = True

class CustomerBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    telephone: Annotated[str, Field(pattern=r'^\+?1?\d{10,15}$')]  # Basic phone number validation

class CustomerCreate(CustomerBase):
    pass

class OrderBase(BaseModel):
    total_amount: float
    status: str
    billing_address_id: int
    shipping_address_id: int

class OrderCreate(OrderBase):
    pass

class Order(OrderBase):
    id: int
    customer_id: int
    order_date: datetime
    billing_address: Address
    shipping_address: Address

    class Config:
        orm_mode = True

class Customer(CustomerBase):
    id: int
    billing_addresses: List[Address] = []
    shipping_addresses: List[Address] = []
    orders: List[Order] = []

    class Config:
        orm_mode = True

class ZipCodeAnalytics(BaseModel):
    zip_code: str
    order_count: int

class TimeOfDayAnalytics(BaseModel):
    hour: int
    order_count: int

class DayOfWeekAnalytics(BaseModel):
    day_of_week: int  # 0 = Monday, 6 = Sunday
    order_count: int 