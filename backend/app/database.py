"""
Database setup and session management
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Database file path
# Use data directory if it exists, otherwise use current directory
base_dir = os.path.dirname(os.path.dirname(__file__))
data_dir = os.path.join(base_dir, "data")
if not os.path.exists(data_dir):
    os.makedirs(data_dir, exist_ok=True)
db_path = os.path.join(data_dir, "shelflife.db")
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{db_path}")

# Configure SQLite with WAL mode for better concurrency
connect_args = {}
if "sqlite" in DATABASE_URL:
    connect_args = {
        "check_same_thread": False,
        "timeout": 20,  # Wait up to 20 seconds for locks
    }

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,  # Verify connections before using them
)

# Enable WAL mode for SQLite to handle concurrent access better
if "sqlite" in DATABASE_URL:
    from sqlalchemy import event
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA busy_timeout=20000")
        cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def init_db():
    """Initialize database tables"""
    from app.models import SystemSettings, Library, Rule, Candidate, ActionLog
    Base.metadata.create_all(bind=engine)
    
    # Migrate existing tables to add new columns if needed
    migrate_database()
    
    # Initialize default settings if none exist
    db = SessionLocal()
    try:
        if db.query(SystemSettings).first() is None:
            default_settings = SystemSettings(
                language="en",
                theme="light",
                auth_enabled=False,
                auth_password_hash=""
            )
            db.add(default_settings)
            db.commit()
    finally:
        db.close()

def migrate_database():
    """Add new columns to existing tables if they don't exist"""
    if "sqlite" not in DATABASE_URL:
        return  # Only SQLite migration for now
    
    from sqlalchemy import text
    conn = engine.connect()
    trans = conn.begin()
    try:
        # Check if candidates table exists
        result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='candidates'"))
        if result.fetchone():
            # Check existing columns
            result = conn.execute(text("PRAGMA table_info(candidates)"))
            existing_columns = [row[1] for row in result.fetchall()]
            
            # Add new columns if they don't exist
            if "show_title" not in existing_columns:
                conn.execute(text("ALTER TABLE candidates ADD COLUMN show_title VARCHAR"))
                print("Added column: candidates.show_title")
            
            if "last_watched_episode_title" not in existing_columns:
                conn.execute(text("ALTER TABLE candidates ADD COLUMN last_watched_episode_title VARCHAR"))
                print("Added column: candidates.last_watched_episode_title")
            
            if "last_watched_episode_number" not in existing_columns:
                conn.execute(text("ALTER TABLE candidates ADD COLUMN last_watched_episode_number INTEGER"))
                print("Added column: candidates.last_watched_episode_number")
            
            if "last_watched_episode_date" not in existing_columns:
                conn.execute(text("ALTER TABLE candidates ADD COLUMN last_watched_episode_date DATETIME"))
                print("Added column: candidates.last_watched_episode_date")
            
            if "episode_count" not in existing_columns:
                conn.execute(text("ALTER TABLE candidates ADD COLUMN episode_count INTEGER"))
                print("Added column: candidates.episode_count")
            
            trans.commit()
    except Exception as e:
        trans.rollback()
        print(f"Migration error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

