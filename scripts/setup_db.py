#!/usr/bin/env python3
"""Database setup script for the Engineering Productivity MVP."""

import sys
import os
from pathlib import Path

# Add src to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from src.data.database import db
from src.config import settings, logger


def setup_database():
    """Initialize the database with all required tables."""
    logger.info("Setting up database...")
    
    try:
        # Database initialization happens automatically in db.__init__()
        # Just verify it's working
        stats = db.get_stats()
        
        logger.info("✅ Database setup completed successfully!")
        logger.info(f"📍 Database location: {settings.database_path}")
        logger.info(f"📊 Current stats: {stats}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Database setup failed: {e}")
        return False


def main():
    """Main setup function."""
    print("🔧 Engineering Productivity MVP - Database Setup")
    print("=" * 50)
    
    success = setup_database()
    
    if success:
        print("\n✅ Setup completed successfully!")
        print("\nNext steps:")
        print("1. ✅ Database is ready!")
        print("2. Run: python scripts/seed_data.py    (optional - adds demo data)")
        print("3. Run: python scripts/run_local.py     (starts the server)")
        print("\nOr use manage.py:")
        print("   python manage.py seed")
        print("   python manage.py run")
    else:
        print("\n❌ Setup failed. Check the logs above.")
        sys.exit(1)


if __name__ == "__main__":
    main()