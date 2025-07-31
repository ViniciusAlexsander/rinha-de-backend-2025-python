from app.queue import payment_queue
from app.processor import process_payment
import logging

logger = logging.getLogger("uvicorn.error")

async def payment_worker(db_pool):
    while True:
        try:
            pagamento = await payment_queue.get()
            amount = pagamento["amount"]
            correlationId = pagamento["correlationId"]
            await process_payment(amount, correlationId, db_pool)
        except Exception as e:
            logger.error("Erro ao processar pagamento na fila: %s", e)
        finally:
            payment_queue.task_done()