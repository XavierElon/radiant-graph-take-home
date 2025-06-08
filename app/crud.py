from sqlalchemy.orm import Session
from sqlalchemy import or_
from . import models, schemas

def get_customer(db: Session, customer_id: int):
    return db.query(models.Customer).filter(models.Customer.id == customer_id).first()

def get_customer_by_email(db: Session, email: str):
    return db.query(models.Customer).filter(models.Customer.email == email).first()

def get_customer_by_telephone(db: Session, telephone: str):
    return db.query(models.Customer).filter(models.Customer.telephone == telephone).first()

def get_customers(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Customer).offset(skip).limit(limit).all()

def create_customer(db: Session, customer: schemas.CustomerCreate):
    db_customer = models.Customer(
        first_name=customer.first_name,
        last_name=customer.last_name,
        email=customer.email,
        telephone=customer.telephone
    )
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer

def create_customer_address(db: Session, address: schemas.AddressCreate, customer_id: int, is_billing: bool = False):
    db_address = models.Address(
        **address.model_dump(),
        billing_customer_id=customer_id if is_billing else None,
        shipping_customer_id=customer_id if not is_billing else None
    )
    db.add(db_address)
    db.commit()
    db.refresh(db_address)
    return db_address

def get_customer_addresses(db: Session, customer_id: int):
    return db.query(models.Address).filter(
        or_(
            models.Address.billing_customer_id == customer_id,
            models.Address.shipping_customer_id == customer_id
        )
    ).all()

def search_customers(db: Session, query: str):
    return db.query(models.Customer).filter(
        or_(
            models.Customer.email.ilike(f"%{query}%"),
            models.Customer.telephone.ilike(f"%{query}%"),
            models.Customer.first_name.ilike(f"%{query}%"),
            models.Customer.last_name.ilike(f"%{query}%")
        )
    ).all() 