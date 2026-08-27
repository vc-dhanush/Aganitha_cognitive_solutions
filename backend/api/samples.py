import json
import os

from fastapi import APIRouter, HTTPException

router = APIRouter()

SAMPLES_DIR = os.path.join(os.path.dirname(__file__), "..", "samples")


@router.get("/sample-images")
def sample_images() -> dict:
    samples = []
    if os.path.isdir(SAMPLES_DIR):
        for name in sorted(os.listdir(SAMPLES_DIR)):
            if name.lower().endswith((".png", ".jpg", ".jpeg", ".tif", ".tiff")):
                samples.append(
                    {
                        "id": os.path.splitext(name)[0],
                        "filename": name,
                        "url": f"/api/samples/{name}",
                    }
                )
    return {"samples": samples}


@router.get("/samples/{filename}")
def get_sample_file(filename: str):
    from fastapi.responses import FileResponse

    safe_name = os.path.basename(filename)
    path = os.path.join(SAMPLES_DIR, safe_name)
    if not os.path.isfile(path):
        raise HTTPException(status_code=404, detail="Sample not found")
    return FileResponse(path)


@router.get("/demo-result")
def demo_result() -> dict:
    demo_path = os.path.join(SAMPLES_DIR, "demo_result.json")
    if not os.path.isfile(demo_path):
        raise HTTPException(status_code=404, detail="Demo result not available")
    with open(demo_path, "r", encoding="utf-8") as handle:
        return json.load(handle)
