from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from .. import schemas
from ..database import get_db
from ..services import analytics_service

router = APIRouter(
    prefix="/analytics",
    tags=["analytics"]
)

@router.get("/orders/zip-code/", response_model=List[schemas.ZipCodeAnalytics])
def get_orders_by_zip_code(
    address_type: str = Query("billing", description="Type of address to analyze (billing or shipping)"),
    order_by: str = Query("desc", description="Sort order (asc or desc)"),
    db: Session = Depends(get_db)
):
    """
    Get order count aggregated by zip code.
    Can be filtered by billing or shipping address and sorted ascending or descending.

    Parameters:
        address_type (str): Type of address to analyze (billing or shipping)
        order_by (str): Sort order (asc or desc)
        db (Session): Database session

    Returns:
        List[ZipCodeAnalytics]: List of zip code analytics with order counts
    """
    return analytics_service.get_orders_by_zip_code(db=db, address_type=address_type, order_by=order_by)

@router.get("/orders/time-of-day/", response_model=List[schemas.TimeOfDayAnalytics])
def get_orders_by_time_of_day(
    limit: int = Query(10, description="Number of hours to return"),
    db: Session = Depends(get_db)
):
    """
    Get order count aggregated by hour of day.
    Returns the top N busiest hours.

    Parameters:
        limit (int): Number of hours to return
        db (Session): Database session

    Returns:
        List[TimeOfDayAnalytics]: List of time of day analytics with order counts
    """
    return analytics_service.get_orders_by_time_of_day(db=db, limit=limit)

@router.get("/orders/day-of-week/", response_model=List[schemas.DayOfWeekAnalytics])
def get_orders_by_day_of_week(
    limit: int = Query(7, description="Number of days to return"),
    db: Session = Depends(get_db)
):
    """
    Get order count aggregated by day of week.
    Returns all days ordered by count (0 = Monday, 6 = Sunday).

    Parameters:
        limit (int): Number of days to return
        db (Session): Database session

    Returns:
        List[DayOfWeekAnalytics]: List of day of week analytics with order counts
    """
    return analytics_service.get_orders_by_day_of_week(db=db, limit=limit)

@router.get("/customers/top-in-store/", response_model=List[schemas.TopInStoreCustomerAnalytics])
def get_top_in_store_customers(
    limit: int = Query(5, description="Number of top customers to return"),
    db: Session = Depends(get_db)
):
    """
    Get top customers by number of in-store orders.
    Returns the top N customers with the most in-store orders.

    Parameters:
        limit (int): Number of top customers to return
        db (Session): Database session

    Returns:
        List[TopInStoreCustomerAnalytics]: List of top in-store customer analytics
    """
    return analytics_service.get_top_in_store_customers(db=db, limit=limit) 