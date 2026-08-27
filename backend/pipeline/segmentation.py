"""Cell segmentation backends."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np

from backend.models.model_manager import MODEL_MANAGER


@dataclass
class SegmentationResult:
    masks: np.ndarray
    model_name: str
    model_type: str
    metadata: dict[str, Any] = field(default_factory=dict)


class SegmentationModel:
    def segment(self, image: np.ndarray, params: dict[str, Any]) -> SegmentationResult:
        raise NotImplementedError


class CellposeModel(SegmentationModel):
    def segment(self, image: np.ndarray, params: dict[str, Any]) -> SegmentationResult:
        model_type = params.get("model_type", "cyto")
        gpu = bool(params.get("gpu", False))
        diameter = params.get("diameter")
        flow_threshold = float(params.get("flow_threshold", 0.4))
        cellprob_threshold = float(params.get("cellprob_threshold", 0.0))

        if MODEL_MANAGER.cellpose_available:
            model = MODEL_MANAGER.get_cellpose_model(model_type=model_type, gpu=gpu)
            diam = None if diameter in (None, 0, "auto", "Auto") else float(diameter)
            masks, flows, styles = model.eval(
                image,
                diameter=diam,
                flow_threshold=flow_threshold,
                cellprob_threshold=cellprob_threshold,
                channels=[0, 0],
            )
            if masks.ndim == 3:
                masks = masks[0]
            return SegmentationResult(
                masks=masks.astype(np.int32),
                model_name="cellpose",
                model_type=model_type,
                metadata={
                    "diameter": diam,
                    "flow_threshold": flow_threshold,
                    "cellprob_threshold": cellprob_threshold,
                    "gpu": gpu,
                    "backend": "cellpose",
                },
            )

        diam_val = diameter
        if diam_val in (None, 0, "auto", "Auto"):
            diam_int = 30
        else:
            diam_int = int(float(diam_val))
        masks = MODEL_MANAGER.run_watershed_fallback(image, diameter=diam_int)
        return SegmentationResult(
            masks=masks,
            model_name="watershed_fallback",
            model_type="classical",
            metadata={
                "backend": "watershed_fallback",
                "reason": MODEL_MANAGER.cellpose_error or "Cellpose unavailable",
            },
        )


class UnetModel(SegmentationModel):
    def segment(self, image: np.ndarray, params: dict[str, Any]) -> SegmentationResult:
        raise NotImplementedError("U-Net backend is not implemented in this MVP")


class StarDistModel(SegmentationModel):
    def segment(self, image: np.ndarray, params: dict[str, Any]) -> SegmentationResult:
        raise NotImplementedError("StarDist backend is not implemented in this MVP")


def get_segmentation_model(name: str) -> SegmentationModel:
    registry = {
        "cellpose": CellposeModel(),
        "unet": UnetModel(),
        "stardist": StarDistModel(),
    }
    key = name.lower()
    if key not in registry:
        raise ValueError(f"Unknown segmentation model: {name}")
    return registry[key]
