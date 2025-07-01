FROM python:3.11-slim

WORKDIR /api

RUN apt-get update && apt-get install -y netcat-openbsd

COPY api/requirements.txt /api/requirements.txt
RUN pip install --no-cache-dir -r /api/requirements.txt

COPY api /api
COPY shared /shared
COPY api/wait_for_postgres.sh /wait.sh
RUN chmod +x /wait.sh

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000"]
