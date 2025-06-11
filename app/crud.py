from sqlalchemy.orm import Session
from . import schemas
from .queries import customer_queries

def get_customer(db: Session, customer_id: int):
    return customer_queries.get_customer(db, customer_id)

def get_customer_by_email(db: Session, email: str):
    return customer_queries.get_customer_by_email(db, email)

def get_customer_by_telephone(db: Session, telephone: str):
    return customer_queries.get_customer_by_telephone(db, telephone)

def get_customers(db: Session, skip: int = 0, limit: int = 100):
    return customer_queries.get_customers(db, skip, limit)

def create_customer(db: Session, customer: schemas.CustomerCreate):
    return customer_queries.create_customer(db, customer)

def create_customer_address(db: Session, address: schemas.AddressCreate, customer_id: int, is_billing: bool = False):
    return customer_queries.create_customer_address(db, address, customer_id, is_billing)

def get_customer_addresses(db: Session, customer_id: int):
    return customer_queries.get_customer_addresses(db, customer_id)

def search_customers(db: Session, query: str):
    return customer_queries.search_customers(db, query) 