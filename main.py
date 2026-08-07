import os
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel

# Database URL from Environment Variable (or default for local testing)
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres:postgres@localhost:5432/postgres"
)

# SQLAlchemy Setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Model
class MessageDB(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, index=True)

# Create tables
Base.metadata.create_all(bind=engine)

# FastAPI App
app = FastAPI(title="Argo Deep Dive API")

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic Schemas
class MessageCreate(BaseModel):
    text: str

class MessageResponse(BaseModel):
    id: int
    text: str

@app.get("/")
def read_root():
    return {"message": "Welcome to the Argo CD Deep Dive API!"}

@app.get("/info")
def get_info():
    """Returns dynamic app info like the version tag"""
    return {
        "app_name": "Argo Deep Dive",
        "version": os.getenv("APP_VERSION", "1.0.0"),
        "database_connected": True
    }

@app.post("/messages", response_model=MessageResponse)
def create_message(msg: MessageCreate, db: Session = Depends(get_db)):
    """Add a message to the database (Data Persistence Test)"""
    new_message = MessageDB(text=msg.text)
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    return new_message

@app.get("/messages", response_model=list[MessageResponse])
def get_messages(db: Session = Depends(get_db)):
    """Retrieve all messages from the database"""
    return db.query(MessageDB).all()
