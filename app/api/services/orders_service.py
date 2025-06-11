from sqlalchemy.orm import Session
from sqlalchemy import or_, func, extract
from ... import models, schemas
from typing import List
from .customers_service import get_customer, get_customer_addresses
from ..queries import orders_queries

def create_order(db: Session, order: schemas.OrderCreate, customer_id: int):
    # Create the order
    order_dict = order.dict()
    shipping_addresses = order_dict.pop('shipping_addresses')
    db_order = models.Order(
        **order_dict,
        customer_id=customer_id
    )
    db.add(db_order)
    db.flush()  # Flush to get the order ID
    
    # Create shipping address entries
    for shipping_addr in shipping_addresses:
        db_shipping_addr = models.OrderShippingAddress(
            order_id=db_order.id,
            address_id=shipping_addr["address_id"],
            sequence=shipping_addr["sequence"]
        )
        db.add(db_shipping_addr)
    
    db.commit()
    db.refresh(db_order)
    return db_order

def get_order(db: Session, order_id: int):
    return orders_queries.get_order_query(db, order_id)

def get_customer_orders(db: Session, customer_id: int, skip: int = 0, limit: int = 100):
    return orders_queries.get_customer_orders_query(db, customer_id, skip, limit)

def search_orders(db: Session, query: str, skip: int = 0, limit: int = 100):
    return orders_queries.search_orders_query(db, query, skip, limit)

def get_orders(db: Session, skip: int = 0, limit: int = 100):
    return orders_queries.get_orders_query(db, skip, limit)

def get_orders_by_time_of_day(db: Session, limit: int = 10):
    """
    Get order count aggregated by hour of day
    Returns the top N busiest hours
    """
    hours_with_orders = orders_queries.get_orders_by_time_of_day_query(db)

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
    days_with_orders = orders_queries.get_orders_by_day_of_week_query(db)

    all_days = {day: 0 for day in range(7)}
    for day, count in days_with_orders:
        all_days[int(day)] = count

    nonzero = [ {"day_of_week": day, "order_count": count} for day, count in all_days.items() if count > 0 ]
    zero = [ {"day_of_week": day, "order_count": 0} for day, count in all_days.items() if count == 0 ]
    nonzero.sort(key=lambda x: (-x["order_count"], x["day_of_week"]))
    zero.sort(key=lambda x: x["day_of_week"])
    result = (nonzero + zero)[:limit]
    return result

def get_top_in_store_customers(db: Session, limit: int = 5):
    """
    Get top customers by number of in-store orders
    Returns the top N customers with the most in-store orders
    """
    return orders_queries.get_top_in_store_customers_query(db, limit)
