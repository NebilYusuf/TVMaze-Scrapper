from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from .db import Base, engine, get_db
from . import models  # registers models
from .ingest_one import ingest_single_show

app = FastAPI(title="TVMaze Scraper API")

Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"status": "ok"}

@app.post("/ingest-one")
async def ingest_one(show_id: int = 1, db: Session = Depends(get_db)):
    result = await ingest_single_show(db, show_id=show_id)
    return result
