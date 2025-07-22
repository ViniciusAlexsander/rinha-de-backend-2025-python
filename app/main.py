from fastapi import FastAPI, HTTPException
from app.db import get_db_pool
from app.models import TransacaoRequest
from app.processor import process_payment
import logging
import traceback

logger = logging.getLogger("uvicorn.error")
db_pool = None
async def lifespan(app: FastAPI):
    global db_pool
    db_pool = await get_db_pool()
    try:
        async with db_pool.acquire() as conn:
            await conn.execute("SELECT 1")
        print("Conexão com o banco OK")
    except Exception as e:
        print("Erro ao conectar no banco:", e)
    yield
    await db_pool.close()

app = FastAPI(lifespan=lifespan)

@app.post("/payments")
async def payments(payload: TransacaoRequest):
    try:
        resultado = await process_payment(payload.valor, db_pool)
        return {"status": "ok", "detalhes": resultado}
    except Exception as e:
        logger.error("Erro no processamento do pagamento: %s", e)
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    print("API está no ar")
    return {"message": "API está no ar"}


