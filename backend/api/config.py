from fastapi import APIRouter

from backend.models.model_manager import MODEL_MANAGER

router = APIRouter()


@router.get("/config")
def config() -> dict:
    return {
        "models": {
            "cellpose": {
                "available": MODEL_MANAGER.cellpose_available,
                "error": MODEL_MANAGER.cellpose_error,
                "types": ["cyto", "cyto2", "nuclei"],
            },
            "unet": {"available": False, "status": "coming_soon"},
            "stardist": {"available": False, "status": "coming_soon"},
        },
        "max_upload_mb": 50,
        "supported_formats": [".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp"],
    }
