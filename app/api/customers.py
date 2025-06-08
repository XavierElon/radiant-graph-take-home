from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import crud, schemas
from ..database import get_db

router = APIRouter(
    prefix="/customers",
    tags=["customers"]
)

@router.post("/", response_model=schemas.Customer)
def create_customer(customer: schemas.CustomerCreate, db: Session = Depends(get_db)):
    db_customer = crud.get_customer_by_email(db, email=customer.email)
    if db_customer:
        raise HTTPException(status_code=400, detail="Email already registered")
    db_customer = crud.get_customer_by_telephone(db, telephone=customer.telephone)
    if db_customer:
        raise HTTPException(status_code=400, detail="Telephone number already registered")
    return crud.create_customer(db=db, customer=customer)

@router.get("/", response_model=List[schemas.Customer])
def read_customers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    customers = crud.get_customers(db, skip=skip, limit=limit)
    return customers

@router.get("/{customer_id}", response_model=schemas.Customer)
def read_customer(customer_id: int, db: Session = Depends(get_db)):
    db_customer = crud.get_customer(db, customer_id=customer_id)
    if db_customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return db_customer

@router.post("/{customer_id}/addresses/", response_model=schemas.Address)
def create_address(
    customer_id: int,
    address: schemas.AddressCreate,
    is_billing: bool = False,
    db: Session = Depends(get_db)
):
    db_customer = crud.get_customer(db, customer_id=customer_id)
    if db_customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return crud.create_customer_address(db=db, address=address, customer_id=customer_id, is_billing=is_billing)

@router.get("/{customer_id}/addresses/", response_model=List[schemas.Address])
def read_customer_addresses(customer_id: int, db: Session = Depends(get_db)):
    db_customer = crud.get_customer(db, customer_id=customer_id)
    if db_customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return crud.get_customer_addresses(db=db, customer_id=customer_id)

@router.get("/search/{query}", response_model=List[schemas.Customer])
def search_customers(query: str, db: Session = Depends(get_db)):
    return crud.search_customers(db=db, query=query) 