import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import redis, json, time, os
from sqlalchemy import create_engine, update
from sqlalchemy.orm import Session
from shared.models import Task, Base   # reuse model

# connect same DB
POSTGRES_URI = (
    f"postgresql://{os.getenv('DB_USER','postgres')}:"
    f"{os.getenv('DB_PASS','postgres')}@"
    f"{os.getenv('DB_HOST','postgres')}:5432/"
    f"{os.getenv('DB_NAME','tasks_db')}"
)
engine = create_engine(POSTGRES_URI, echo=False, future=True)
Base.metadata.create_all(engine)

r = redis.Redis(host=os.getenv("REDIS_HOST","redis"), port=6379, decode_responses=True)

print("🎯 Worker started, waiting for jobs…")

while True:
    _, raw = r.brpop("task_queue")            # blocking pop
    data = json.loads(raw)
    print("🔧  processing", data)

    # pretend work
    time.sleep(4)

    # update DB (e.g., mark done)
    with Session(engine) as s:
        stmt = update(Task).where(Task.id == data["id"]).values(text=data["text"] + " ✅ processed")
        s.execute(stmt)
        s.commit()
