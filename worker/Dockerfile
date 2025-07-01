FROM python:3.11-slim


WORKDIR /worker
RUN apt-get update && apt-get install -y netcat-openbsd && apt-get clean

COPY worker/requirements.txt /worker/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY worker /worker
COPY shared /shared

COPY worker/wait_for_postgres.sh /wait.sh
RUN chmod +x /wait.sh

CMD ["/wait.sh", "python", "worker.py"]
