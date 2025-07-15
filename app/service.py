from sqlalchemy.orm import Session
from . import models, schemas

def create_payment(db: Session, payment: schemas.PaymentCreate):
    db_payment = models.Payments(correlationId=payment.correlationId, amount=payment.amount)
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)

def get_payment(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Payments).offset(skip).limit(limit).all()
    
