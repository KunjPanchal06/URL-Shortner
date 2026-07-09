from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL is None:
    raise ValueError("DATABASE URL is not set")

engine = create_engine(DATABASE_URL)

session_local = sessionmaker(
    bind=engine,
    autoflush=False
)

class Base(DeclarativeBase):
    pass