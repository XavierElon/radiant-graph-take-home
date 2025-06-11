from sqlalchemy.orm import Session
from sqlalchemy import func, desc, asc, extract
from .. import models, schemas

def get_orders_by_zip_code_query(db: Session, address_type: str = "billing", order_by: str = "desc"):
    """
    Get order count aggregated by zip code query.
    
    Args:
        db: Database session
        address_type: Type of address to analyze (billing or shipping)
        order_by: Sort order (asc or desc)
    
    Returns:
        Query object for zip code analytics
    """
    address_field = models.Order.billing_address_id if address_type == "billing" else models.Order.shipping_address_id
    
    query = db.query(
        models.Address.zip_code,
        func.count(models.Order.id).label('order_count')
    ).join(
        models.Order,
        address_field == models.Address.id
    ).group_by(
        models.Address.zip_code
    )
    
    if order_by.lower() == "asc":
        query = query.order_by(asc('order_count'))
    else:
        query = query.order_by(desc('order_count'))
    
    return query

def get_orders_by_time_of_day_query(db: Session):
    """
    Get order count aggregated by hour of day query.
    
    Args:
        db: Database session
    
    Returns:
        Query object for time of day analytics
    """
    return db.query(
        extract('hour', models.Order.order_date).label('hour'),
        func.count(models.Order.id).label('order_count')
    ).group_by(
        extract('hour', models.Order.order_date)
    )

def get_orders_by_day_of_week_query(db: Session):
    """
    Get order count aggregated by day of week query.
    
    Args:
        db: Database session
    
    Returns:
        Query object for day of week analytics
    """
    return db.query(
        extract('dow', models.Order.order_date).label('day_of_week'),
        func.count(models.Order.id).label('order_count')
    ).group_by(
        extract('dow', models.Order.order_date)
    )

def get_top_in_store_customers_query(db: Session, limit: int = 5):
    """
    Get top customers by number of in-store orders query.
    
    Args:
        db: Database session
        limit: Number of top customers to return
    
    Returns:
        Query object for top in-store customer analytics
    """
    return db.query(
        models.Customer.id.label('customer_id'),
        models.Customer.first_name,
        models.Customer.last_name,
        models.Customer.email,
        func.count(models.Order.id).label('in_store_order_count')
    ).join(
        models.Order,
        models.Order.customer_id == models.Customer.id
    ).filter(
        models.Order.order_type == 'in_store'
    ).group_by(
        models.Customer.id,
        models.Customer.first_name,
        models.Customer.last_name,
        models.Customer.email
    ).order_by(
        desc('in_store_order_count')
    ).limit(limit)
