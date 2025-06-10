from sqlalchemy.orm import Session
from sqlalchemy import func, desc, asc, extract
from .. import models, schemas
from datetime import datetime, timezone

def get_orders_by_zip_code(db: Session, address_type: str = "billing", order_by: str = "desc"):
    """
    Get order count aggregated by zip code.
    
    Args:
        db: Database session
        address_type: Type of address to analyze (billing or shipping)
        order_by: Sort order (asc or desc)
    
    Returns:
        List of zip code analytics with order counts
    """
    # Select the appropriate address field based on address_type
    address_field = models.Order.billing_address_id if address_type == "billing" else models.Order.shipping_address_id
    
    # Base query to get zip codes and counts
    query = db.query(
        models.Address.zip_code,
        func.count(models.Order.id).label('order_count')
    ).join(
        models.Order,
        address_field == models.Address.id
    ).group_by(
        models.Address.zip_code
    )
    
    # Apply sorting
    if order_by.lower() == "asc":
        query = query.order_by(asc('order_count'))
    else:
        query = query.order_by(desc('order_count'))
    
    results = query.all()
    
    return [
        schemas.ZipCodeAnalytics(
            zip_code=zip_code,
            order_count=count
        ) for zip_code, count in results
    ]

def get_orders_by_time_of_day(db: Session, limit: int = 10):
    """
    Get order count aggregated by hour of day.
    
    Args:
        db: Database session
        limit: Number of hours to return
    
    Returns:
        List of time of day analytics with order counts
    """
    # Get all hours with their counts
    results = db.query(
        extract('hour', models.Order.order_date).label('hour'),
        func.count(models.Order.id).label('order_count')
    ).group_by(
        extract('hour', models.Order.order_date)
    ).all()

    # Create a dictionary of all hours with zero counts
    all_hours = {hour: 0 for hour in range(24)}
    
    # Update with actual counts
    for hour, count in results:
        all_hours[int(hour)] = count

    # Convert to list and sort by count (desc) and hour (asc)
    sorted_hours = sorted(
        [{"hour": hour, "order_count": count} for hour, count in all_hours.items()],
        key=lambda x: (-x["order_count"], x["hour"])
    )

    # Return top N hours
    return [
        schemas.TimeOfDayAnalytics(
            hour=item["hour"],
            order_count=item["order_count"]
        ) for item in sorted_hours[:limit]
    ]

def get_orders_by_day_of_week(db: Session, limit: int = 7):
    """
    Get order count aggregated by day of week.
    
    Args:
        db: Database session
        limit: Number of days to return
    
    Returns:
        List of day of week analytics with order counts
    """
    # Get all days with their counts
    results = db.query(
        extract('dow', models.Order.order_date).label('day_of_week'),
        func.count(models.Order.id).label('order_count')
    ).group_by(
        extract('dow', models.Order.order_date)
    ).all()

    # Create a dictionary of all days with zero counts
    all_days = {day: 0 for day in range(7)}
    
    # Update with actual counts
    for day, count in results:
        all_days[int(day)] = count

    # Convert to list and sort by count (desc) and day (asc)
    sorted_days = sorted(
        [{"day_of_week": day, "order_count": count} for day, count in all_days.items()],
        key=lambda x: (-x["order_count"], x["day_of_week"])
    )

    # Return top N days
    return [
        schemas.DayOfWeekAnalytics(
            day_of_week=item["day_of_week"],
            order_count=item["order_count"]
        ) for item in sorted_days[:limit]
    ]

def get_top_in_store_customers(db: Session, limit: int = 5):
    """
    Get top customers by number of in-store orders.
    
    Args:
        db: Database session
        limit: Number of top customers to return
    
    Returns:
        List of top in-store customer analytics
    """
    results = db.query(
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
    ).limit(limit).all()
    
    return [
        schemas.TopInStoreCustomerAnalytics(
            customer_id=customer_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            in_store_order_count=count
        ) for customer_id, first_name, last_name, email, count in results
    ]
