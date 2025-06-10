from sqlalchemy import create_engine, text
from app.database import SQLALCHEMY_DATABASE_URL

def upgrade():
    """Add order_type column to orders table."""
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    with engine.begin() as conn:
        # Add order_type column with default value
        conn.execute(text("""
            ALTER TABLE orders 
            ADD COLUMN order_type VARCHAR NOT NULL DEFAULT 'online'
        """))

def downgrade():
    """Remove order_type column from orders table."""
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    with engine.begin() as conn:
        conn.execute(text("""
            ALTER TABLE orders 
            DROP COLUMN order_type
        """))

if __name__ == "__main__":
    upgrade() 