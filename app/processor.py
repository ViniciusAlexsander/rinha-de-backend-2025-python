import httpx
import datetime
import uuid

DEFAULT_URL = "http://localhost:8001/payments"
FALLBACK_URL = "http://localhost:8002/payments"

async def process_payment(amount: float):
    payload = {
        "correlationId": str(uuid.uuid4()),
        "amount": amount,
        "requestedAt": datetime.datetime.utcnow().isoformat() + "Z"
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
