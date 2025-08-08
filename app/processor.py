import httpx
from datetime import datetime, timezone
import asyncpg
from app.models import PaymentIn, PaymentsSummaryResponse, SummaryItem

DEFAULT_URL = "http://payment-processor-default:8080/payments"
FALLBACK_URL = "http://payment-processor-fallback:8080/payments"

async def process_payment(amount: float, correlationId: str, db_pool: asyncpg.pool.Pool):
    requested_at = datetime.now(timezone.utc)
    
    payload = {
        "correlationId": correlationId,
        "amount": amount,
        "requestedAt": requested_at.isoformat()
    }
    headers = {"Content-Type": "application/json"}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(DEFAULT_URL, json=payload, headers=headers, timeout=5)
            response.raise_for_status()
            payment_obj = PaymentIn(
                correlationId=correlationId,
                amount=amount,
                requestedAt=requested_at,
                processorType="default"
            )
            await create_payment(payment_obj, db_pool)
            return
        except Exception:
            response = await client.post(FALLBACK_URL, json=payload, headers=headers, timeout=5)
            response.raise_for_status()
            payment_obj = PaymentIn(
                correlationId=correlationId,
                amount=amount,
                requestedAt=requested_at,
                processorType="fallback"
            )
            await create_payment(payment_obj, db_pool)
            return

_insert_payment_query = """
            INSERT INTO payments (correlation_id, amount, requested_at, processor_type)
            VALUES ($1, $2, $3, $4)
        """

async def create_payment(payment: PaymentIn, db_pool: asyncpg.pool.Pool):
    async with db_pool.acquire() as conn:
        await conn.execute(_insert_payment_query, payment.correlationId, payment.amount, payment.requestedAt, payment.processorType)

async def get_payments_summary(db_pool: asyncpg.pool.Pool, from_date: datetime=None, to_date: datetime=None):
    
    _get_payments_summary_query = """SELECT processor_type, COUNT(*) AS total_requests, SUM(amount) AS total_amount FROM payments"""
    conditions = []
    params = []

    if from_date is not None:
        params.append(from_date)
        conditions.append(f"requested_at >= ${len(params)}")

    if to_date is not None:
        params.append(to_date)
        conditions.append(f"requested_at <= ${len(params)}")
    
    if conditions:
        _get_payments_summary_query += " WHERE " + " AND ".join(conditions)

    _get_payments_summary_query += " GROUP BY processor_type"

    print(_get_payments_summary_query)
    
    async with db_pool.acquire() as conn:
        result = await conn.fetch(_get_payments_summary_query, *params)

    print("Query Result:", result)

    default_summary = SummaryItem()
    fallback_summary = SummaryItem()
    for row in result:
        if row['processor_type'] == "default":
            default_summary.totalRequests = row['total_requests']
            default_summary.totalAmount = float(row['total_amount']) if row['total_amount'] is not None else 0.0
        
        if row['processor_type'] == "fallback":
            fallback_summary.totalRequests = row['total_requests']
            fallback_summary.totalAmount = float(row['total_amount']) if row['total_amount'] is not None else 0.0

    return PaymentsSummaryResponse(default=default_summary, fallback=fallback_summary)