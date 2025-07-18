from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.processor import process_payment

app = FastAPI()

class TransacaoRequest(BaseModel):
    valor: float

@app.post("/payments")
async def payments(payload: TransacaoRequest):
    try:
        resultado = await process_payment(payload.valor)
        return {"status": "ok", "detalhes": resultado}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "API está no ar"}


