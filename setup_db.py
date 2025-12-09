"""Database setup script - creates database and tables."""
import sys
from sqlalchemy import create_engine, text
from app.database import Base, LOCAL_DB_URL
from app.models import Vehicle

def create_database():
    """Create the vehicles database if it doesn't exist."""
    db_name = "vehicles"
    postgres_url = LOCAL_DB_URL.rsplit("/", 1)[0]  # Remove database name
    admin_engine = create_engine(f"{postgres_url}/postgres", isolation_level="AUTOCOMMIT")
    
    with admin_engine.connect() as conn:
        # Check if database exists
        result = conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname = :db_name"),
            {"db_name": db_name}
        )
        exists = result.fetchone()
        
        if not exists:
            conn.execute(text(f'CREATE DATABASE {db_name}'))
            print(f"✓ Created database '{db_name}'")
        else:
            print(f"✓ Database '{db_name}' already exists")
    
    admin_engine.dispose()

def create_tables():
    """Create all tables in the database."""
    engine = create_engine(LOCAL_DB_URL)
    Base.metadata.create_all(bind=engine)
    print("✓ Created tables")
    engine.dispose()

if __name__ == "__main__":
    print("Setting up database...")
    try:
        create_database()
        create_tables()
        print("\n✓ Database setup complete!")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\nMake sure PostgreSQL is running and credentials are correct.")
        sys.exit(1)

