from sqlalchemy import Column, Integer, String, Float
from .database import Base

class Payments(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    correlationId = Column(String, index=True)
    amount = Column(Float, unique=False, index=True)

