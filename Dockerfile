FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt debugpy

COPY . .

EXPOSE 8080 5678


CMD ["sh", "-c", "\
  if [ \"$DEBUG\" = \"true\" ]; then \
    python -m debugpy --listen 0.0.0.0:5678 --wait-for-client --log-to-stderr -m uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload; \
  else \
    uvicorn app.main:app --host 0.0.0.0 --port 8080; \
  fi"]