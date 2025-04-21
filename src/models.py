# src/models.py
from sqlalchemy import Column, Integer, String, create_engine, MetaData, Table
from sqlalchemy.ext.declarative import declarative_base

DATABASE_URL = "sqlite:///./functions.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
Base = declarative_base()

class Function(Base):
    __tablename__ = "functions"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    route = Column(String)
    language = Column(String)
    timeout = Column(Integer)  # Timeout in seconds
    filename = Column(String)  # NEW: stores name like 'hello.py'


# Create the database tables
def init_db():
    Base.metadata.create_all(bind=engine)
