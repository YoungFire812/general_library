UNIQUE_VIOLATION = "23505"
FOREIGN_KEY_VIOLATION = "23503"
NOT_NULL_VIOLATION = "23502"


async def is_error(e, state):
    if getattr(e.orig, "sqlstate", None) == state:
        return True
    else:
        return False
