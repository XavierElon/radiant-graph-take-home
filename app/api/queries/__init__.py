"""
Database query layer for the application
"""

from .health_queries import check_database_connection

__all__ = ['check_database_connection'] 