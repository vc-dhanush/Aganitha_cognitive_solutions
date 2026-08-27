import json

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from backend.pipeline.analyzer import run_analysis
from backend.utils.image_utils import validate_upload

router = APIRouter()


@router.post("/analyze")
async def analyze(
    file: UploadFile = File(...),
    params: str = Form("{}"),
) -> dict:
    try:
        config = json.loads(params or "{}")
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail="Invalid params JSON") from exc

    content = await file.read()
    filename = file.filename or "upload.png"
    try:
        validate_upload(filename, content)
        return run_analysis(content, filename, config)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except NotImplementedError as exc:
        raise HTTPException(status_code=501, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Analysis failed. Check image format and backend configuration.",
        ) from exc
