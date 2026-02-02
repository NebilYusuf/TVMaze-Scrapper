from sqlalchemy.orm import Session
from .models import Show, CastMember
from .tvmaze_client import TVMazeClient

def extract_person(cast_item: dict) -> dict:
    """
    TVMaze /shows/{id}/cast returns items like:
    { "person": {...}, "character": {...}, ... }
    We only need person fields.
    """
    person = cast_item.get("person") or {}
    return {
        "id": person.get("id"),
        "name": person.get("name") or "",
        "birthday": person.get("birthday"),  # may be None
    }

async def ingest_single_show(db: Session, show_id: int = 1) -> dict:
    client = TVMazeClient()
    try:
        show_data = await client.get_show(show_id)
        cast_data = await client.get_show_cast(show_id)

        # Upsert show
        show = db.get(Show, show_id)
        if show is None:
            show = Show(id=show_id, name=show_data.get("name") or "")
            db.add(show)
        else:
            show.name = show_data.get("name") or show.name

        db.commit()

        # Replace cast (simple & clear for learning)
        db.query(CastMember).filter(CastMember.show_id == show_id).delete()

        people = [extract_person(x) for x in cast_data]
        for p in people:
            seen = set()
            for item in cast_data:
                p = extract_person(item)
                if p["id"] is None:
                    continue

                pid = int(p["id"])
                if pid in seen:
                    continue
                seen.add(pid)

                db.add(
                    CastMember(
                        person_id=pid,
                        show_id=show_id,
                        name=p["name"],
                        birthday=p["birthday"],
                    )
                )


        db.commit()

        return {
            "show_id": show_id,
            "show_name": show.name,
            "cast_count": len(people),
        }
    finally:
        await client.close()
