from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ... import schemas
from ...database import get_db
from ..services import orders_service

router = APIRouter(
    prefix="/orders",
    tags=["orders"]
)

@router.post("/customers/{customer_id}/orders/", response_model=schemas.Order)
def create_order(
    customer_id: int,
    order: schemas.OrderCreate,
    db: Session = Depends(get_db)
):
    db_customer = orders_service.get_customer(db, customer_id=customer_id)
    if db_customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Verify billing address exists and belongs to customer
    billing_address = orders_service.get_customer_addresses(db, customer_id=customer_id)
    if not any(addr.id == order.billing_address_id for addr in billing_address):
        raise HTTPException(status_code=400, detail="Invalid billing address")
    
    # Verify all shipping addresses exist and belong to customer
    shipping_addresses = orders_service.get_customer_addresses(db, customer_id=customer_id)
    for shipping_addr in order.shipping_addresses:
        if not any(addr.id == shipping_addr.address_id for addr in shipping_addresses):
            raise HTTPException(status_code=400, detail=f"Invalid shipping address ID: {shipping_addr.address_id}")
    
    return orders_service.create_order(db=db, order=order, customer_id=customer_id)

@router.get("/customers/{customer_id}/orders/", response_model=List[schemas.Order])
def read_customer_orders(
    customer_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    db_customer = orders_service.get_customer(db, customer_id=customer_id)
    if db_customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return orders_service.get_customer_orders(db=db, customer_id=customer_id, skip=skip, limit=limit)

@router.get("/search/", response_model=List[schemas.Order])
def search_orders(
    query: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return orders_service.search_orders(db=db, query=query, skip=skip, limit=limit)

@router.get("/{order_id}", response_model=schemas.Order)
def read_order(order_id: int, db: Session = Depends(get_db)):
    db_order = orders_service.get_order(db, order_id=order_id)
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return db_order

@router.get("/", response_model=List[schemas.Order])
def read_orders(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all orders with pagination."""
    return orders_service.get_orders(db=db, skip=skip, limit=limit) 