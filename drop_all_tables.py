"""
Script to drop all tables and recreate from scratch
"""
from sqlmodel import create_engine, text, SQLModel
from app.core.config import settings

def drop_all_tables():
    print("Dropping all existing tables...")
    engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))
    
    try:
        with engine.connect() as conn:
            # Drop all tables
            conn.execute(text("DROP SCHEMA public CASCADE"))
            conn.execute(text("CREATE SCHEMA public"))
            conn.execute(text("GRANT ALL ON SCHEMA public TO postgres"))
            conn.execute(text("GRANT ALL ON SCHEMA public TO public"))
            conn.commit()
            print("✅ All tables dropped successfully!")
    except Exception as e:
        print(f"Error: {e}")
        raise

if __name__ == "__main__":
    drop_all_tables()
