from sqlalchemy.orm import Session
from sqlalchemy import or_, func, extract
from ... import models, schemas

def create_order_query(db: Session, order_data: dict, customer_id: int):
    db_order = models.Order(
        **order_data,
        customer_id=customer_id
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order

def get_order_query(db: Session, order_id: int):
    return db.query(models.Order).filter(models.Order.id == order_id).first()

def get_customer_orders_query(db: Session, customer_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Order).filter(
        models.Order.customer_id == customer_id
    ).offset(skip).limit(limit).all()

def search_orders_query(db: Session, search_pattern: str, skip: int = 0, limit: int = 100):
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

def get_orders_by_zip_code_query(db: Session, address_id, order_by: str = "desc"):
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

def get_orders_by_time_of_day_query(db: Session):
    return db.query(
        extract('hour', models.Order.order_date).label('hour'),
        func.count(models.Order.id).label('order_count')
    ).group_by(
        extract('hour', models.Order.order_date)
    ).all()

def get_orders_by_day_of_week_query(db: Session):
    return db.query(
        extract('dow', models.Order.order_date).label('day_of_week'),
        func.count(models.Order.id).label('order_count')
    ).group_by(
        extract('dow', models.Order.order_date)
    ).all()

def get_top_in_store_customers_query(db: Session, limit: int = 5):
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
        func.count(models.Order.id).desc()
    ).limit(limit).all()

def get_orders_query(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Order).offset(skip).limit(limit).all()


