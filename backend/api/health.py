from fastapi import APIRouter

from backend.models.model_manager import MODEL_MANAGER

router = APIRouter()


@router.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "service": "microscopyai",
        "cellpose_available": MODEL_MANAGER.cellpose_available,
        "cellpose_error": MODEL_MANAGER.cellpose_error,
    }
