from .anime import router as anime_router
from .level import router as level_router
from .song import router as song_router
from .source import router as source_router
from .timing import router as timing_router

routers = [anime_router, song_router, source_router, timing_router, level_router]
__all__ = [routers]
