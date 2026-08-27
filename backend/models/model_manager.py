"""Segmentation model manager with lazy loading and caching."""

from __future__ import annotations

import logging
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)

_CELLPOSE_MODEL = None
_CELLPOSE_AVAILABLE = False
_CELLPOSE_ERROR: str | None = None

try:
    from cellpose import models as cellpose_models

    _CELLPOSE_AVAILABLE = True
except Exception as exc:  # noqa: BLE001
    _CELLPOSE_ERROR = str(exc)
    logger.warning("Cellpose not available: %s", exc)


class ModelManager:
    """Loads and caches segmentation backends."""

    def __init__(self) -> None:
        self._cellpose_cache: dict[str, Any] = {}

    @property
    def cellpose_available(self) -> bool:
        return _CELLPOSE_AVAILABLE

    @property
    def cellpose_error(self) -> str | None:
        return _CELLPOSE_ERROR

    def get_cellpose_model(self, model_type: str = "cyto", gpu: bool = False) -> Any:
        if not _CELLPOSE_AVAILABLE:
            raise RuntimeError(
                _CELLPOSE_ERROR or "Cellpose is not installed on this server"
            )
        key = f"{model_type}_{gpu}"
        if key not in self._cellpose_cache:
            self._cellpose_cache[key] = cellpose_models.CellposeModel(
                gpu=gpu, model_type=model_type
            )
        return self._cellpose_cache[key]

    def run_watershed_fallback(self, image: np.ndarray, diameter: int | None = None) -> np.ndarray:
        """Classical fallback segmentation when Cellpose is unavailable."""
        from scipy import ndimage as ndi
        from skimage.feature import peak_local_max
        from skimage.filters import threshold_otsu
        from skimage.measure import label
        from skimage.segmentation import watershed

        img = image.astype(np.float32)
        blur = cv2.GaussianBlur(img, (0, 0), 1.5)
        try:
            thresh_val = threshold_otsu(blur)
        except ValueError:
            thresh_val = blur.mean()
        thresh = blur > thresh_val
        distance = ndi.distance_transform_edt(thresh)
        min_distance = max(8, (diameter or 30) // 2)
        coords = peak_local_max(distance, min_distance=min_distance, labels=thresh)
        if len(coords) == 0:
            return label(thresh).astype(np.int32)
        mask = np.zeros(distance.shape, dtype=np.int32)
        for idx, (y, x) in enumerate(coords, start=1):
            mask[y, x] = idx
        labels = watershed(-distance, mask, mask=thresh)
        return labels.astype(np.int32)


# Late import for watershed fallback
import cv2  # noqa: E402

MODEL_MANAGER = ModelManager()
