from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from . import  schemas, service
from .database import SessionLocal, engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/payments/", response_model=list[schemas.PaymentRead])
def get_payment(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return service.get_payment(db, skip=skip, limit=limit)

@app.post("/payments")
def create_payment(payment: schemas.PaymentCreate, db: Session = Depends(get_db)):
    return service.create_payment(db=db, payment=payment)