from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

class TransacaoRequest(BaseModel):
    valor: float

class PaymentIn(BaseModel):
    correlationId: UUID
    amount: float
    requestedAt: datetime