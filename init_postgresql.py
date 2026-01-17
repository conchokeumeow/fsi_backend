"""
PostgreSQL Database Initialization Script
Tạo tables và dữ liệu mặc định cho PostgreSQL database
"""
from sqlmodel import SQLModel, select, Session

from app.core.config import settings
from app.core.db import engine
from app.core.security import get_password_hash
from app.models.role import Role
from app.models.user import User


def create_tables():
    """Tạo tất cả các bảng trong database"""
    print("🔨 Creating database tables...")
    
    # Import all models để SQLModel biết cần tạo tables nào
    import app.models  # This imports all models from __init__.py
    
    # Create all tables
    SQLModel.metadata.create_all(engine)
    print("✅ Tables created successfully!\n")


def create_default_roles():
    """Tạo các role mặc định"""
    print("👥 Creating default roles...")
    
    with Session(engine) as session:
        # Check if roles already exist
        result = session.exec(select(Role))
        existing_roles = result.all()
        
        if existing_roles:
            print("ℹ️  Roles already exist, skipping...\n")
            return
        
        # Create default roles
        roles = [
            Role(
                role_id=1,
                name="Admin",
                is_superuser=True
            ),
            Role(
                role_id=2,
                name="Teacher",
                is_superuser=False
            ),
        ]
        
        for role in roles:
            session.add(role)
        
        session.commit()
        print(f"✅ Created {len(roles)} default roles\n")


def create_superuser():
    """Tạo tài khoản superuser từ environment variables"""
    print("🔑 Creating superuser account...")
    
    with Session(engine) as session:
        # Check if superuser already exists
        result = session.exec(
            select(User).where(User.username == settings.FIRST_SUPERUSER_USERNAME)
        )
        existing_user = result.first()
        
        if existing_user:
            print(f"ℹ️  Superuser already exists: {settings.FIRST_SUPERUSER_USERNAME}\n")
            return
        
        # Validate required settings
        if not settings.FIRST_SUPERUSER_USERNAME or not settings.FIRST_SUPERUSER_PASSWORD:
            print("❌ ERROR: FIRST_SUPERUSER_USERNAME and FIRST_SUPERUSER_PASSWORD must be set in .env file")
            return
        
        # Create superuser
        superuser = User(
            username=settings.FIRST_SUPERUSER_USERNAME,
            password_hash=get_password_hash(settings.FIRST_SUPERUSER_PASSWORD),
            email=settings.FIRST_SUPERUSER_EMAIL,
            role_id=1,  # Admin role
            is_active=True,
        )
        
        session.add(superuser)
        session.commit()
        session.refresh(superuser)
        
        print(f"✅ Superuser created successfully!")
        print(f"   Username: {superuser.username}")
        print(f"   Email: {superuser.email}")
        print(f"   Role: Admin\n")


def init_db():
    """Main initialization function"""
    print("\n" + "="*60)
    print("🚀 FSI Academic System - PostgreSQL Database Initialization")
    print("="*60 + "\n")
    
    # Verify PostgreSQL connection
    print(f"📊 Database: {settings.POSTGRES_DB}")
    print(f"🖥️  Server: {settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}")
    print(f"👤 User: {settings.POSTGRES_USER}\n")
    
    try:
        # Step 1: Create tables
        create_tables()
        
        # Step 2: Create default roles
        create_default_roles()
        
        # Step 3: Create superuser
        create_superuser()
        
        print("="*60)
        print("🎉 Database initialization completed successfully!")
        print("="*60)
        print("\n📝 Next steps:")
        print("   1. Start the server: fastapi dev app/main.py")
        print("   2. Open API docs: http://localhost:8000/api/v1/docs")
        print("   3. Login with superuser credentials")
        print("\n")
        
    except Exception as e:
        print("\n" + "="*60)
        print("❌ ERROR during initialization:")
        print("="*60)
        print(f"\n{type(e).__name__}: {str(e)}\n")
        print("💡 Troubleshooting:")
        print("   1. Check PostgreSQL is running")
        print("   2. Verify database credentials in .env file")
        print("   3. Ensure database exists and user has permissions")
        print("   4. Check DEPLOYMENT_POSTGRESQL.md for detailed guide\n")
        raise


if __name__ == "__main__":
    print("\n🔧 Checking environment configuration...")
    
    # Check database type
    if settings.POSTGRES_SERVER == "sqlite":
        print("\n⚠️  WARNING: You are using SQLite configuration!")
        print("   This script is for PostgreSQL initialization.")
        print("   For SQLite, use: python init_sqlite.py\n")
        exit(1)
    
    print(f"✅ Environment: {settings.ENVIRONMENT}")
    print(f"✅ Database type: PostgreSQL\n")
    
    # Run initialization
    init_db()
