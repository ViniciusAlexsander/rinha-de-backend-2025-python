from app.queue import payment_queue
from app.processor import process_payment
import logging
import asyncio

logger = logging.getLogger("uvicorn.error")

MAX_CONCURRENT_PAYMENTS = 20

async def handle_payment(pagamento, db_pool):
    try:
        amount = pagamento["amount"]
        correlationId = pagamento["correlationId"]
        await process_payment(amount, correlationId, db_pool)
    except Exception as e:
        logger.error("Erro ao processar pagamento: %s", e)
    finally:
        payment_queue.task_done()

async def payment_worker(db_pool):
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_PAYMENTS)

    async def worker_task():
        while True:
            pagamento = await payment_queue.get()
            await semaphore.acquire()
            asyncio.create_task(process_with_semaphore(pagamento, db_pool, semaphore))

    await worker_task()

async def process_with_semaphore(pagamento, db_pool, semaphore):
    async with semaphore:
        await handle_payment(pagamento, db_pool)
        semaphore.release()