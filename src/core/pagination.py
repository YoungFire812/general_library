from fastapi import Query


class Pagination:
    def __init__(
        self, page: int = Query(1, ge=1), limit: int = Query(24, ge=1, le=100)
    ):
        self.page = page
        self.limit = limit
