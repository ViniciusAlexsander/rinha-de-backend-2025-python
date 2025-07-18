from pydantic import BaseModel

class TransacaoRequest(BaseModel):
    valor: float
