from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, Query


@dataclass
class PageParams:
    limit: int
    offset: int


def page_params(
    limit: Annotated[int, Query(ge=1, le=50)] = 10,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> PageParams:
    return PageParams(limit=limit, offset=offset)


Pagination = Annotated[PageParams, Depends(page_params)]
