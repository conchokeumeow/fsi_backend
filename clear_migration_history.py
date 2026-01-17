"""
Script to clear alembic version history
Run this to fix migration history issues
"""
from sqlmodel import create_engine, text
from app.core.config import settings

def clear_alembic_history():
    print("Clearing alembic version history...")
    engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))
    
    try:
        with engine.connect() as conn:
            # Delete old migration references
            conn.execute(text("DELETE FROM alembic_version"))
            conn.commit()
            print("✅ Alembic version history cleared successfully!")
    except Exception as e:
        print(f"⚠️  Note: {e}")
        print("This is OK if alembic_version table doesn't exist yet")

if __name__ == "__main__":
    clear_alembic_history()
