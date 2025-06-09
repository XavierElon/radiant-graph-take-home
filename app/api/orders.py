from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import crud, schemas
from ..database import get_db

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
    db_customer = crud.get_customer(db, customer_id=customer_id)
    if db_customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Verify billing and shipping addresses exist and belong to customer
    billing_address = crud.get_customer_addresses(db, customer_id=customer_id)
    shipping_address = crud.get_customer_addresses(db, customer_id=customer_id)
    
    if not any(addr.id == order.billing_address_id for addr in billing_address):
        raise HTTPException(status_code=400, detail="Invalid billing address")
    if not any(addr.id == order.shipping_address_id for addr in shipping_address):
        raise HTTPException(status_code=400, detail="Invalid shipping address")
    
    return crud.create_order(db=db, order=order, customer_id=customer_id)

@router.get("/customers/{customer_id}/orders/", response_model=List[schemas.Order])
def read_customer_orders(
    customer_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    db_customer = crud.get_customer(db, customer_id=customer_id)
    if db_customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return crud.get_customer_orders(db=db, customer_id=customer_id, skip=skip, limit=limit)

@router.get("/search/", response_model=List[schemas.Order])
def search_orders(
    query: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return crud.search_orders(db=db, query=query, skip=skip, limit=limit)

@router.get("/{order_id}", response_model=schemas.Order)
def read_order(order_id: int, db: Session = Depends(get_db)):
    db_order = crud.get_order(db, order_id=order_id)
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return db_order 