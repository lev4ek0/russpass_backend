from fastapi import APIRouter

from app.api.endpoints.search import router as search_router
# from app.ws import router as ws_router

api_router = APIRouter()
api_router.include_router(
    search_router,
    prefix="/search",
    tags=["Поиск"],
)

