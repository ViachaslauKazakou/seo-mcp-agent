"""Database manager for PostgreSQL connections."""

import os
from contextlib import contextmanager
from typing import Generator, Optional
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import QueuePool

from .models import Base


class DatabaseManager:
    """Manager for database connections and sessions."""
    
    def __init__(
        self,
        database_url: Optional[str] = None,
        echo: bool = False,
        pool_size: int = 5,
        max_overflow: int = 10,
    ):
        """
        Initialize database manager.
        
        Args:
            database_url: PostgreSQL connection URL. If None, reads from env.
            echo: Whether to echo SQL queries (for debugging).
            pool_size: Number of connections to keep in pool.
            max_overflow: Max connections to create beyond pool_size.
        """
        if database_url is None:
            database_url = self._get_database_url_from_env()
        
        self.database_url = database_url
        self.echo = echo
        
        # Create engine
        self.engine = create_engine(
            database_url,
            echo=echo,
            poolclass=QueuePool,
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_pre_ping=True,  # Verify connections before using
        )
        
        # Create session factory
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine,
        )
    
    @staticmethod
    def _get_database_url_from_env() -> str:
        """Build database URL from environment variables."""
        db_user = os.getenv("POSTGRES_USER", "docker")
        db_password = os.getenv("POSTGRES_PASSWORD", "docker")
        db_host = os.getenv("POSTGRES_HOST", "localhost")
        db_port = os.getenv("POSTGRES_PORT", "5434")
        db_name = os.getenv("POSTGRES_DB", "postgres")
        
        return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    
    def create_tables(self) -> None:
        """Create all tables in the database."""
        Base.metadata.create_all(bind=self.engine)
    
    def drop_tables(self) -> None:
        """Drop all tables from the database."""
        Base.metadata.drop_all(bind=self.engine)
    
    def get_session(self) -> Session:
        """
        Get a new database session.
        
        Returns:
            SQLAlchemy Session instance.
        """
        return self.SessionLocal()
    
    @contextmanager
    def session_scope(self) -> Generator[Session, None, None]:
        """
        Provide a transactional scope around a series of operations.
        
        Usage:
            with db_manager.session_scope() as session:
                # Do database operations
                session.add(obj)
                # Commit happens automatically on success
                # Rollback happens automatically on exception
        
        Yields:
            SQLAlchemy Session instance.
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    def check_connection(self) -> bool:
        """
        Check if database connection is working.
        
        Returns:
            True if connection is successful, False otherwise.
        """
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception as e:
            print(f"Database connection failed: {e}")
            return False
    
    def close(self) -> None:
        """Close all database connections."""
        self.engine.dispose()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


# Global database manager instance
_db_manager: Optional[DatabaseManager] = None


def get_db_manager(
    database_url: Optional[str] = None,
    echo: bool = False,
) -> DatabaseManager:
    """
    Get global database manager instance.
    
    Args:
        database_url: PostgreSQL connection URL. If None, reads from env.
        echo: Whether to echo SQL queries.
    
    Returns:
        DatabaseManager instance.
    """
    global _db_manager
    
    if _db_manager is None:
        _db_manager = DatabaseManager(database_url=database_url, echo=echo)
    
    return _db_manager


def get_session() -> Session:
    """
    Get database session (for FastAPI dependencies).
    
    Usage in FastAPI:
        @app.get("/items")
        def get_items(session: Session = Depends(get_session)):
            return session.query(Item).all()
    
    Returns:
        SQLAlchemy Session instance.
    """
    db_manager = get_db_manager()
    session = db_manager.get_session()
    try:
        yield session
    finally:
        session.close()
