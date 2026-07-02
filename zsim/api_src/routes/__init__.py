from fastapi import APIRouter

from .buff_graph import router as buff_graph_router

router = APIRouter()

router.include_router(buff_graph_router, tags=["BuffGraph"])
