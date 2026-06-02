FROM python:3.11-slim

WORKDIR /app

# Install system dependencies needed for compiling certain python packages
RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# Install ONLY backend-specific dependencies directly
RUN pip install --no-cache-dir \
    fastapi==0.110.0 \
    "uvicorn[standard]==0.28.0" \
    sqlalchemy==2.0.28 \
    psycopg2-binary==2.9.9 \
    pydantic==2.6.4 \
    pydantic-settings==2.2.1 \
    tenacity==8.2.3

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

