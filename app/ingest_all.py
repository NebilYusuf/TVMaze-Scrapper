import asyncio
from sqlalchemy.orm import Session
from sqlalchemy import select

from .models import Show, CastMember
from .tvmaze_client import TVMazeClient
from .ingest_one import extract_person  # reuse the same extractor
from .db import SessionLocal



async def ingest_all_shows(db: Session, concurrency: int = 6, max_pages: int | None = None) -> dict:
    """
    Scrape ALL shows from TVMaze:
      - /shows?page=0,1,2,... until empty
      - for each show: fetch cast and store
    """
    client = TVMazeClient()
    total_shows_processed = 0
    page = 0

    # Limits how many /cast requests run at once
    sem = asyncio.Semaphore(concurrency)

    try:
        while True:
            if max_pages is not None and page >= max_pages:
                break

            shows = await client.list_shows_by_page(page)
            if not shows:
                break

            # 1) Upsert shows in this page
            show_ids = []
            for s in shows:
                show_id = int(s["id"])
                show_ids.append(show_id)

                existing = db.get(Show, show_id)
                if existing is None:
                    db.add(Show(id=show_id, name=s.get("name") or ""))
                else:
                    existing.name = s.get("name") or existing.name

            db.commit()

            # 2) Fetch + store cast concurrently (bounded by semaphore)
            async def fetch_and_store_cast(show_id: int):
                async with sem:
                    cast_data = await client.get_show_cast(show_id)

                # NEW: each task gets its own DB session
                local_db = SessionLocal()
                try:
                    local_db.query(CastMember).filter(
                        CastMember.show_id == show_id
                    ).delete()

                    seen = set()
                    for item in cast_data:
                        p = extract_person(item)
                        if p["id"] is None:
                            continue

                        pid = int(p["id"])
                        key = (pid, show_id)
                        if key in seen:
                            continue
                        seen.add(key)

                        local_db.add(
                            CastMember(
                                person_id=pid,
                                show_id=show_id,
                                name=p["name"],
                                birthday=p["birthday"],
                            )
                        )

                    local_db.commit()
                finally:
                    local_db.close()



            await asyncio.gather(*[fetch_and_store_cast(sid) for sid in show_ids])

            total_shows_processed += len(show_ids)
            page += 1

        return {
            "pages_scraped": page,
            "shows_processed": total_shows_processed,
            "concurrency": concurrency,
            "max_pages": max_pages,
        }

    finally:
        await client.close()
