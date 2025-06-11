from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ... import schemas
from ...database import get_db
from ..services import customers_service

router = APIRouter(
    prefix="/customers",
    tags=["customers"]
)

@router.post("/", response_model=schemas.Customer)
def create_customer(customer: schemas.CustomerCreate, db: Session = Depends(get_db)):
    """
    Create a new customer in the database.
    Checks for duplicate email and telephone numbers before creation.

    Parameters:
        customer (CustomerCreate): Customer data to create
        db (Session): Database session

    Returns:
        Customer: The created customer object

    Raises:
        HTTPException: If email or telephone number is already registered
    """
    db_customer = customers_service.get_customer_by_email(db, email=customer.email)
    if db_customer:
        raise HTTPException(status_code=400, detail="Email already registered")
    db_customer = customers_service.get_customer_by_telephone(db, telephone=customer.telephone)
    if db_customer:
        raise HTTPException(status_code=400, detail="Telephone number already registered")
    return customers_service.create_customer(db=db, customer=customer)

@router.get("/", response_model=List[schemas.Customer])
def read_customers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Get a list of customers with pagination support.

    Parameters:
        skip (int): Number of records to skip (for pagination)
        limit (int): Maximum number of records to return
        db (Session): Database session

    Returns:
        List[Customer]: List of customer objects
    """
    customers = customers_service.get_customers(db, skip=skip, limit=limit)
    return customers

@router.get("/{customer_id}", response_model=schemas.Customer)
def read_customer(customer_id: int, db: Session = Depends(get_db)):
    """
    Get a specific customer by their ID.

    Parameters:
        customer_id (int): ID of the customer to retrieve
        db (Session): Database session

    Returns:
        Customer: The requested customer object

    Raises:
        HTTPException: If customer is not found
    """
    db_customer = customers_service.get_customer(db, customer_id=customer_id)
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
    """
    Create a new address for a specific customer.

    Parameters:
        customer_id (int): ID of the customer to add the address to
        address (AddressCreate): Address data to create
        is_billing (bool): Whether this is a billing address
        db (Session): Database session

    Returns:
        Address: The created address object

    Raises:
        HTTPException: If customer is not found
    """
    db_customer = customers_service.get_customer(db, customer_id=customer_id)
    if db_customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customers_service.create_customer_address(db=db, address=address, customer_id=customer_id, is_billing=is_billing)

@router.get("/{customer_id}/addresses/", response_model=List[schemas.Address])
def read_customer_addresses(customer_id: int, db: Session = Depends(get_db)):
    """
    Get all addresses for a specific customer.

    Parameters:
        customer_id (int): ID of the customer to get addresses for
        db (Session): Database session

    Returns:
        List[Address]: List of address objects for the customer

    Raises:
        HTTPException: If customer is not found
    """
    db_customer = customers_service.get_customer(db, customer_id=customer_id)
    if db_customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customers_service.get_customer_addresses(db=db, customer_id=customer_id)

@router.get("/search/{query}", response_model=List[schemas.Customer])
def search_customers(query: str, db: Session = Depends(get_db)):
    """
    Search for customers based on a query string.

    Parameters:
        query (str): Search query string
        db (Session): Database session

    Returns:
        List[Customer]: List of matching customer objects
    """
    return customers_service.search_customers(db=db, query=query) 