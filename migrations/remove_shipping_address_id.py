"""Migration to remove shipping_address_id from orders table."""

from sqlalchemy import create_engine, text
from app.database import SQLALCHEMY_DATABASE_URL

def migrate():
    """Remove shipping_address_id column from orders table."""
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    
    with engine.begin() as connection:
        # Drop the foreign key constraint if it exists
        connection.execute(text("""
            DO $$ 
            BEGIN
                IF EXISTS (
                    SELECT 1 
                    FROM information_schema.table_constraints 
                    WHERE constraint_name = 'orders_shipping_address_id_fkey'
                ) THEN
                    ALTER TABLE orders DROP CONSTRAINT orders_shipping_address_id_fkey;
                END IF;
            END $$;
        """))
        
        # Drop the column
        connection.execute(text("""
            ALTER TABLE orders DROP COLUMN IF EXISTS shipping_address_id;
        """))

if __name__ == "__main__":
    migrate() 