"""Image loading, validation, and conversion utilities."""

from __future__ import annotations

import io
import os
import tempfile
from typing import Any

import cv2
import numpy as np
from PIL import Image

ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp"}
MAX_UPLOAD_BYTES = 50 * 1024 * 1024


def validate_upload(filename: str, content: bytes) -> None:
    ext = os.path.splitext(filename.lower())[1]
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {ext or 'unknown'}")
    if len(content) > MAX_UPLOAD_BYTES:
        raise ValueError(f"File exceeds maximum size of {MAX_UPLOAD_BYTES // (1024 * 1024)} MB")
    if len(content) == 0:
        raise ValueError("Empty file uploaded")


def load_image_from_bytes(content: bytes) -> tuple[np.ndarray, np.ndarray, dict[str, Any]]:
    """Load image bytes into a BGR uint8 array and metadata dict."""
    try:
        pil_image = Image.open(io.BytesIO(content))
    except Exception as exc:
        raise ValueError("Could not decode image file") from exc

    meta: dict[str, Any] = {
        "channels": len(pil_image.getbands()),
        "mode": pil_image.mode,
        "width": pil_image.width,
        "height": pil_image.height,
    }

    if pil_image.mode in ("I;16", "I"):
        meta["bit_depth"] = 16
        arr = np.array(pil_image)
        if arr.dtype != np.uint16:
            arr = arr.astype(np.uint16)
        if arr.ndim == 2:
            bgr = cv2.cvtColor(arr, cv2.COLOR_GRAY2BGR)
        else:
            bgr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
        display = normalize_to_uint8(arr if arr.ndim == 2 else arr[:, :, 0])
    else:
        meta["bit_depth"] = 8
        rgb = np.array(pil_image.convert("RGB"))
        bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
        display = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)

    meta["image_type"] = infer_image_type(meta)
    return bgr, display, meta


def infer_image_type(meta: dict[str, Any]) -> str:
    mode = meta.get("mode", "")
    if mode in ("L", "I;16", "I"):
        return "brightfield"
    return "fluorescence"


def normalize_to_uint8(image: np.ndarray) -> np.ndarray:
    if image.dtype == np.uint8:
        return image
    img = image.astype(np.float32)
    min_val, max_val = float(img.min()), float(img.max())
    if max_val <= min_val:
        return np.zeros_like(image, dtype=np.uint8)
    scaled = (img - min_val) / (max_val - min_val)
    return (scaled * 255).astype(np.uint8)


def to_grayscale(image_bgr: np.ndarray) -> np.ndarray:
    if image_bgr.ndim == 2:
        return image_bgr
    return cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)


def encode_image_png(image: np.ndarray) -> bytes:
    if image.ndim == 2:
        ok, buf = cv2.imencode(".png", image)
    else:
        ok, buf = cv2.imencode(".png", image)
    if not ok:
        raise ValueError("Failed to encode image")
    return buf.tobytes()


def encode_image_base64(image: np.ndarray) -> str:
    import base64

    return base64.b64encode(encode_image_png(image)).decode("ascii")


def save_temp_upload(content: bytes, suffix: str = ".png") -> str:
    fd, path = tempfile.mkstemp(suffix=suffix, prefix="microscopyai_")
    os.close(fd)
    with open(path, "wb") as handle:
        handle.write(content)
    return path
