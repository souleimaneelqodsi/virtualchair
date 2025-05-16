from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from flask import current_app


from .config import Config


db_uri = Config.SQLALCHEMY_DATABASE_URI

if not db_uri:
    print(
        "SQLALCHEMY_DATABASE_URI is not set. Please check your .env file and config.py."
    )
    engine = None
else:
    try:
        engine = create_engine(db_uri)
    except Exception as e:
        print(f"Error creating database engine: {e}")
        engine = None


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
