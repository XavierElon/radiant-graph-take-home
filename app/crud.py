from sqlalchemy.orm import Session
from sqlalchemy import or_, func, extract
from . import models, schemas
from datetime import datetime, time
from typing import List

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
        **address.dict(),
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

def create_order(db: Session, order: schemas.OrderCreate, customer_id: int):
    db_order = models.Order(
        **order.dict(),
        customer_id=customer_id
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order

def get_order(db: Session, order_id: int):
    return db.query(models.Order).filter(models.Order.id == order_id).first()

def get_customer_orders(db: Session, customer_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Order).filter(
        models.Order.customer_id == customer_id
    ).offset(skip).limit(limit).all()

def search_orders(db: Session, query: str, skip: int = 0, limit: int = 100) -> List[models.Order]:
    """Search orders by customer email or phone number."""
    # Remove any leading/trailing whitespace and ensure the query is not empty
    query = query.strip()
    if not query:
        return []

    # Format the search pattern
    search_pattern = f"%{query}%"

    # Query orders with customer information
    return (
        db.query(models.Order)
        .join(models.Customer)
        .filter(
            or_(
                models.Customer.email.ilike(search_pattern),
                models.Customer.telephone.ilike(search_pattern)
            )
        )
        .offset(skip)
        .limit(limit)
        .all()
    )

def get_orders_by_zip_code(db: Session, address_type: str = "billing", order_by: str = "desc"):
    """
    Get order count aggregated by zip code
    address_type: "billing" or "shipping"
    order_by: "asc" or "desc"
    """
    if address_type == "billing":
        address_id = models.Order.billing_address_id
    else:
        address_id = models.Order.shipping_address_id

    query = db.query(
        models.Address.zip_code,
        func.count(models.Order.id).label('order_count')
    ).join(
        models.Order,
        address_id == models.Address.id
    ).group_by(
        models.Address.zip_code
    )

    if order_by.lower() == "asc":
        query = query.order_by(func.count(models.Order.id).asc())
    else:
        query = query.order_by(func.count(models.Order.id).desc())

    return query.all()

def get_orders_by_time_of_day(db: Session, limit: int = 10):
    """
    Get order count aggregated by hour of day
    Returns the top N busiest hours
    """
    hours_with_orders = db.query(
        extract('hour', models.Order.order_date).label('hour'),
        func.count(models.Order.id).label('order_count')
    ).group_by(
        extract('hour', models.Order.order_date)
    ).all()

    all_hours = {hour: 0 for hour in range(24)}
    for hour, count in hours_with_orders:
        all_hours[int(hour)] = count

    # First, get all hours with nonzero orders
    nonzero = [ {"hour": hour, "order_count": count} for hour, count in all_hours.items() if count > 0 ]
    # Then, get hours with zero orders
    zero = [ {"hour": hour, "order_count": 0} for hour, count in all_hours.items() if count == 0 ]
    # Sort nonzero by count desc, hour asc; zero by hour asc
    nonzero.sort(key=lambda x: (-x["order_count"], x["hour"]))
    zero.sort(key=lambda x: x["hour"])
    # Combine and slice to limit
    result = (nonzero + zero)[:limit]
    return result

def get_orders_by_day_of_week(db: Session, limit: int = 7):
    """
    Get order count aggregated by day of week
    Returns all days ordered by count (0 = Monday, 6 = Sunday)
    """
    days_with_orders = db.query(
        extract('dow', models.Order.order_date).label('day_of_week'),
        func.count(models.Order.id).label('order_count')
    ).group_by(
        extract('dow', models.Order.order_date)
    ).all()

    all_days = {day: 0 for day in range(7)}
    for day, count in days_with_orders:
        all_days[int(day)] = count

    nonzero = [ {"day_of_week": day, "order_count": count} for day, count in all_days.items() if count > 0 ]
    zero = [ {"day_of_week": day, "order_count": 0} for day, count in all_days.items() if count == 0 ]
    nonzero.sort(key=lambda x: (-x["order_count"], x["day_of_week"]))
    zero.sort(key=lambda x: x["day_of_week"])
    result = (nonzero + zero)[:limit]
    return result 