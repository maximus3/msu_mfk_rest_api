from fastapi import APIRouter

from app.endpoints.v1 import router as v1_router


list_of_routes: list[APIRouter] = [
    v1_router,
]


__all__ = [
    'list_of_routes',
]
