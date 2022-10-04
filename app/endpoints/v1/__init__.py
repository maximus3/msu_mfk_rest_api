from fastapi import APIRouter

from .auth import api_router as auth_router
from .course import api_router as course_router
from .department import api_router as department_router
from .logs import api_router as logs_router
from .ping import api_router as ping_router
from .register import api_router as register_router


prefix = '/v1'
router = APIRouter(
    prefix=prefix,
)

router.include_router(ping_router)
router.include_router(auth_router)
router.include_router(register_router)
router.include_router(logs_router)
router.include_router(course_router)
router.include_router(department_router)


__all__ = [
    'prefix',
    'router',
]
