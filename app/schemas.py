from pydantic import BaseModel

class PaymentCreate(BaseModel):
    correlationId: str 
    amount: float

class PaymentRead(PaymentCreate):
    id: int

    class Config:
        orm_mode = True
