"""Seed script to create initial company and admin user (dev only)."""
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal, engine
from app.db.base import Base
from app.db.models.company import Company
from app.db.models.user import User, UserRole
from app.core.security import hash_password
import uuid


def seed_admin():
    """Create a company and admin user for development."""
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    db: Session = SessionLocal()
    try:
        # Check if company already exists
        company = db.query(Company).filter(Company.name == "Default Company").first()
        
        if not company:
            # Create company
            company = Company(
                id=uuid.uuid4(),
                name="Default Company"
            )
            db.add(company)
            db.commit()
            db.refresh(company)
            print(f"✓ Created company: {company.name} (ID: {company.id})")
        else:
            print(f"✓ Company already exists: {company.name} (ID: {company.id})")
        
        # Check if admin user already exists
        admin_user = db.query(User).filter(
            User.email == "admin@example.com",
            User.company_id == company.id
        ).first()
        
        if not admin_user:
            # Create admin user
            admin_user = User(
                id=uuid.uuid4(),
                company_id=company.id,
                email="admin@example.com",
                password_hash=hash_password("admin123"),  # Change this in production!
                role=UserRole.ADMIN,
                is_active=True
            )
            db.add(admin_user)
            db.commit()
            print(f"✓ Created admin user: {admin_user.email}")
            print(f"  Company ID: {company.id}")
            print(f"  Email: admin@example.com")
            print(f"  Password: admin123")
            print(f"  Role: {admin_user.role.value}")
        else:
            print(f"✓ Admin user already exists: {admin_user.email}")
        
    except Exception as e:
        db.rollback()
        print(f"✗ Error seeding data: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("Seeding admin user and company...")
    seed_admin()
    print("Done!")
