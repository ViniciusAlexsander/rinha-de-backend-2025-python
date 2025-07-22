import httpx
from datetime import datetime, timezone
import uuid
import asyncpg
from app.models import PaymentIn

DEFAULT_URL = "http://payment-processor-default:8080/payments"
FALLBACK_URL = "http://payment-processor-fallback:8080/payments"

async def process_payment(amount: float, db_pool: asyncpg.pool.Pool):
    correlation_id = str(uuid.uuid4())
    requested_at = datetime.now(timezone.utc)

    payment_obj = PaymentIn(
        correlationId=correlation_id,
        amount=amount,
        requestedAt=requested_at
    )
    await create_payment(payment_obj, db_pool)

    payload = {
        "correlationId": correlation_id,
        "amount": amount,
        "requestedAt": requested_at.isoformat()
    }
    headers = {"Content-Type": "application/json"}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(DEFAULT_URL, json=payload, headers=headers, timeout=5)
            response.raise_for_status()
            return response.json()
        except Exception:
            response = await client.post(FALLBACK_URL, json=payload, headers=headers, timeout=5)
            response.raise_for_status()
            return response.json()

async def create_payment(payment: PaymentIn, db_pool: asyncpg.pool.Pool):
    async with db_pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO payments (correlation_id, amount, requested_at)
            VALUES ($1, $2, $3)
        """, payment.correlationId, payment.amount, payment.requestedAt)