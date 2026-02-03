from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from .db import Base, engine, get_db
from . import models  # registers models
from .ingest_one import ingest_single_show

from sqlalchemy import select, func
from .models import Show, CastMember
from .schemas import PaginatedShows, ShowOut, CastOut
from .sort_utils import birthday_sort_key

from .ingest_all import ingest_all_shows

app = FastAPI(title="TVMaze Scraper API")

Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"status": "ok"}

@app.post("/ingest-one")
async def ingest_one(show_id: int = 1, db: Session = Depends(get_db)):
    result = await ingest_single_show(db, show_id=show_id)
    return result

@app.post("/ingest")
async def ingest(
    concurrency: int = 6,
    max_pages: int | None = None,
    db: Session = Depends(get_db),
):
    """
    Ingest all TV shows from TVMaze.
    Use max_pages for testing (e.g. 1 or 2).
    """
    result = await ingest_all_shows(db, concurrency=concurrency, max_pages=max_pages)
    return result

@app.get("/shows", response_model=PaginatedShows)
def get_shows(
    page: int = 1,
    page_size: int = 25,
    db: Session = Depends(get_db),
):
    # total number of shows in DB
    total = db.scalar(select(func.count()).select_from(Show)) or 0

    # pagination math
    offset = (page - 1) * page_size

    shows = db.scalars(
        select(Show).order_by(Show.id).offset(offset).limit(page_size)
    ).all()

    items = []
    for show in shows:
        cast = db.scalars(
            select(CastMember).where(CastMember.show_id == show.id)
        ).all()

        cast_sorted = sorted(
            cast,
            key=lambda c: birthday_sort_key(c.birthday),
            reverse=True
        )

        items.append(
            ShowOut(
                id=show.id,
                name=show.name,
                cast=[
                    CastOut(id=c.person_id, name=c.name, birthday=c.birthday)
                    for c in cast_sorted
                ],
            )
        )

    return PaginatedShows(
        page=page,
        page_size=page_size,
        total=total,
        items=items
    )

