from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, UniqueConstraint, DateTime, Float
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    telephone = Column(String, unique=True, index=True, nullable=False)
    
    # Relationships
    billing_addresses = relationship("Address", back_populates="billing_customer", 
                                   foreign_keys="Address.billing_customer_id")
    shipping_addresses = relationship("Address", back_populates="shipping_customer",
                                    foreign_keys="Address.shipping_customer_id")
    orders = relationship("Order", back_populates="customer")

    __table_args__ = (
        UniqueConstraint('email', name='uq_customer_email'),
        UniqueConstraint('telephone', name='uq_customer_telephone'),
    )

class Address(Base):
    __tablename__ = "addresses"

    id = Column(Integer, primary_key=True, index=True)
    street_address = Column(String, nullable=False)
    apartment_suite = Column(String)
    city = Column(String, nullable=False)
    state = Column(String(2), nullable=False)  # 2-letter state code
    zip_code = Column(String(10), nullable=False)  # Format: 12345 or 12345-6789
    
    # Customer relationships
    billing_customer_id = Column(Integer, ForeignKey("customers.id"))
    shipping_customer_id = Column(Integer, ForeignKey("customers.id"))
    
    # Relationships
    billing_customer = relationship("Customer", back_populates="billing_addresses",
                                  foreign_keys=[billing_customer_id])
    shipping_customer = relationship("Customer", back_populates="shipping_addresses",
                                   foreign_keys=[shipping_customer_id])
    
    # Address type
    is_billing_address = Column(Boolean, default=False)
    is_shipping_address = Column(Boolean, default=True)

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    order_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    total_amount = Column(Float, nullable=False)
    status = Column(String, nullable=False)  # e.g., "pending", "completed", "cancelled"
    
    # Relationships
    customer = relationship("Customer", back_populates="orders")
    billing_address_id = Column(Integer, ForeignKey("addresses.id"), nullable=False)
    shipping_address_id = Column(Integer, ForeignKey("addresses.id"), nullable=False)
    
    billing_address = relationship("Address", foreign_keys=[billing_address_id])
    shipping_address = relationship("Address", foreign_keys=[shipping_address_id]) 