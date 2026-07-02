from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from zsim.api_src.models.buff_graph import (
    BuffGraphAPIResponse,
    BuffGraphCensusRequest,
    BuffGraphCreateRequest,
    BuffGraphStatusRequest,
    BuffGraphUpdateRequest,
    BuffGraphXLogicImportRequest,
)
from zsim.api_src.services.buff_graph_service import BuffGraphService

router = APIRouter()
buff_graph_service = BuffGraphService()


@router.get("/buff-graphs", tags=["BuffGraph"], response_model=BuffGraphAPIResponse)
async def list_buff_graphs():
    return BuffGraphAPIResponse(data=buff_graph_service.list_graphs())


@router.post("/buff-graphs", tags=["BuffGraph"], response_model=BuffGraphAPIResponse)
async def create_buff_graph(request: BuffGraphCreateRequest):
    return BuffGraphAPIResponse(data=buff_graph_service.save_graph(request.spec))


@router.get(
    "/buff-graphs/migration/catalog",
    tags=["BuffGraph"],
    response_model=BuffGraphAPIResponse,
)
async def get_migration_catalog():
    return BuffGraphAPIResponse(data=buff_graph_service.migration_catalog())


@router.post(
    "/buff-graphs/migration/census",
    tags=["BuffGraph"],
    response_model=BuffGraphAPIResponse,
)
async def census_xlogic(request: BuffGraphCensusRequest):
    return BuffGraphAPIResponse(data=buff_graph_service.census_sources(request.sources))


@router.post(
    "/buff-graphs/migration/import-xlogic",
    tags=["BuffGraph"],
    response_model=BuffGraphAPIResponse,
)
async def import_xlogic(request: BuffGraphXLogicImportRequest):
    return BuffGraphAPIResponse(
        data=buff_graph_service.import_xlogic(
            xlogic_path=request.xlogic_path,
            source=request.source,
            owner_kind=request.owner_kind,
            owner_name=request.owner_name,
            source_buff_index=request.source_buff_index,
            graph_id=request.graph_id,
            display_name=request.display_name,
        )
    )


@router.get(
    "/buff-graphs/parity/matrix",
    tags=["BuffGraph"],
    response_model=BuffGraphAPIResponse,
)
async def get_parity_matrix():
    return BuffGraphAPIResponse(data=buff_graph_service.parity_matrix())


@router.post(
    "/buff-graphs/parity/matrix/run",
    tags=["BuffGraph"],
    response_model=BuffGraphAPIResponse,
)
async def run_parity_matrix():
    return BuffGraphAPIResponse(data=buff_graph_service.parity_matrix())


@router.get("/buff-graphs/{graph_id}", tags=["BuffGraph"], response_model=BuffGraphAPIResponse)
async def get_buff_graph(graph_id: str):
    try:
        return BuffGraphAPIResponse(data=buff_graph_service.get_graph(graph_id))
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.put("/buff-graphs/{graph_id}", tags=["BuffGraph"], response_model=BuffGraphAPIResponse)
async def update_buff_graph(graph_id: str, request: BuffGraphUpdateRequest):
    if request.spec.graph_id != graph_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="graph_id in path and request body must match",
        )
    return BuffGraphAPIResponse(data=buff_graph_service.save_graph(request.spec))


@router.post(
    "/buff-graphs/{graph_id}/validate",
    tags=["BuffGraph"],
    response_model=BuffGraphAPIResponse,
)
async def validate_buff_graph(graph_id: str):
    try:
        return BuffGraphAPIResponse(data=buff_graph_service.validate_graph(graph_id))
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.post(
    "/buff-graphs/{graph_id}/compile",
    tags=["BuffGraph"],
    response_model=BuffGraphAPIResponse,
)
async def compile_buff_graph(graph_id: str):
    try:
        return BuffGraphAPIResponse(data=buff_graph_service.compile_graph(graph_id))
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.post(
    "/buff-graphs/{graph_id}/parity",
    tags=["BuffGraph"],
    response_model=BuffGraphAPIResponse,
)
async def request_buff_graph_parity(graph_id: str):
    try:
        return BuffGraphAPIResponse(data=buff_graph_service.request_parity(graph_id))
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.post(
    "/buff-graphs/{graph_id}/status",
    tags=["BuffGraph"],
    response_model=BuffGraphAPIResponse,
)
async def update_buff_graph_status(graph_id: str, request: BuffGraphStatusRequest):
    try:
        return BuffGraphAPIResponse(
            data=buff_graph_service.update_status(
                graph_id,
                runtime_status=request.runtime_status,
                last_verified_at=request.last_verified_at,
            )
        )
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
