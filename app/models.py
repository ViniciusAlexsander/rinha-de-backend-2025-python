from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from typing import Optional

class TransacaoRequest(BaseModel):
    correlationId: str
    amount: float

class PaymentIn(BaseModel):
    correlationId: UUID
    amount: float
    requestedAt: datetime
    processorType: str

class SummaryItem(BaseModel):
    totalRequests: int = 0
    totalAmount: float = 0

class PaymentsSummaryResponse(BaseModel):
    default: SummaryItem
    fallback: SummaryItem