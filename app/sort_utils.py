from dateutil.parser import isoparse

def birthday_sort_key(birthday: str | None):
    """
    Sorting goal:
      - birthdays present first
      - newest birthday first (descending)
      - missing/invalid birthdays last

    We return a tuple so Python can sort reliably.
    """
    if not birthday:
        return (0, None)
    try:
        # convert "YYYY-MM-DD" into a date object
        d = isoparse(birthday).date()
        return (1, d)
    except Exception:
        return (0, None)
