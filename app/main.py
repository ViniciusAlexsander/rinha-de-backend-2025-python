import asyncio
from typing import Optional
from fastapi import FastAPI, HTTPException, Query
from app.db import get_db_pool
from app.models import TransacaoRequest
from app.processor import get_payments_summary
from app.queue import payment_queue
from app.worker import payment_worker
import logging
import traceback
from datetime import datetime

logger = logging.getLogger("uvicorn.error")
db_pool = None
worker_task = None
async def lifespan(app: FastAPI):
    global db_pool
    db_pool = await get_db_pool()
    try:
        async with db_pool.acquire() as conn:
            await conn.execute("SELECT 1")
        print("Conexão com o banco OK")
    except Exception as e:
        print("Erro ao conectar no banco:", e)

    worker_task = asyncio.create_task(payment_worker(db_pool))

    yield
    worker_task.cancel()
    await db_pool.close()

app = FastAPI(lifespan=lifespan)

@app.post("/payments")
async def payments(payload: TransacaoRequest):
    try:
        await payment_queue.put(payload.dict())
        return {"status": "ok", "detalhes": "Pagamento enfileirado"}
    except Exception as e:
        logger.error("Erro no processamento do pagamento: %s", e)
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/payments-summary")
async def payments_summary(    
    from_date: Optional[str] = Query(None, alias="from"),
    to_date: Optional[str] = Query(None, alias="to")
):
    def parse_date(value: Optional[str]) -> Optional[datetime]:
        if not value:
            return None
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            try:
                return datetime.strptime(value, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Formato inválido para data: {value}"
                )

    from_dt = parse_date(from_date)
    to_dt = parse_date(to_date)
    
    return await get_payments_summary(db_pool, from_dt, to_dt)

@app.get("/")
async def root():
    return {"message": "API está no ar?"}


