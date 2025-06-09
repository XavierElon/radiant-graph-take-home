import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def setup_database():
    # Connect to PostgreSQL server using Docker Compose credentials
    conn = psycopg2.connect(
        user="radiant",
        password="radiant123",
        host="localhost",
        port="5433",  # Note: Using 5433 as specified in docker-compose.yml
        database="radiant_graph"
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    
    try:
        # Create database if it doesn't exist
        cur.execute("SELECT 1 FROM pg_database WHERE datname = 'radiant_graph'")
        exists = cur.fetchone()
        if not exists:
            cur.execute("CREATE DATABASE radiant_graph")
            print("Database 'radiant_graph' created successfully")
        else:
            print("Database 'radiant_graph' already exists")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    setup_database() 