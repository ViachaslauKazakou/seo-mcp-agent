#!/usr/bin/env python3
"""Database initialization script."""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from db.manager import DatabaseManager


def init_database():
    """Initialize database with all tables."""
    print("🔧 Initializing database...")
    
    # Create database manager
    db_manager = DatabaseManager(echo=True)
    
    # Check connection
    print("📡 Checking database connection...")
    if not db_manager.check_connection():
        print("❌ Failed to connect to database!")
        print("Make sure PostgreSQL is running and environment variables are set.")
        sys.exit(1)
    
    print("✅ Database connection successful!")
    
    # Create tables
    print("📋 Creating database tables...")
    try:
        db_manager.create_tables()
        print("✅ All tables created successfully!")
    except Exception as e:
        print(f"❌ Failed to create tables: {e}")
        sys.exit(1)
    finally:
        db_manager.close()
    
    print("\n🎉 Database initialization complete!")
    print("\nCreated tables:")
    print("  - websites")
    print("  - analysis_runs")
    print("  - keywords")
    print("  - keyword_clusters")
    print("  - serp_results")
    print("  - serp_positions")
    print("  - page_analyses")


if __name__ == "__main__":
    init_database()
