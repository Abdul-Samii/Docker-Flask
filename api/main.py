import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, Session
import redis
import json
import os
import uvicorn

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL:
    POSTGRES_URI = DATABASE_URL          # full Neon string
else:
    POSTGRES_URI = (
        f"postgresql://{os.getenv('DB_USER','postgres')}:"
        f"{os.getenv('DB_PASS','postgres')}@"
        f"{os.getenv('DB_HOST','postgres')}:5432/"
        f"{os.getenv('DB_NAME','tasks_db')}"
    )

engine = create_engine(POSTGRES_URI, echo=True, future=True)
Base = declarative_base()

class Task(Base):
    __tablename__ = "tasks"
    id   = Column(Integer, primary_key=True, autoincrement=True)
    text = Column(String, nullable=False)

Base.metadata.create_all(engine)

redis_client = redis.Redis(host=os.getenv("REDIS_HOST","redis"), port=6379, db=0, decode_responses=True)

app = FastAPI()

class TaskIn(BaseModel):
    text: str

@app.post("/tasks")
def create_task(task: TaskIn):
    with Session(engine) as session:
        db_task = Task(text=task.text)
        session.add(db_task)
        session.commit()
        session.refresh(db_task)

    # enqueue for worker
    redis_client.lpush("task_queue", json.dumps({"id": db_task.id, "text": db_task.text}))
    return {"msg": "task queued", "id": db_task.id}

@app.get("/tasks/{task_id}")
def read_task(task_id: int):
    with Session(engine) as session:
        t = session.get(Task, task_id)
        if not t:
            raise HTTPException(status_code=404, detail="Task not found")
        return {"id": t.id, "text": t.text}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=5000)