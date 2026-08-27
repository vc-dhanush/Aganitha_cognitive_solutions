"""Full analysis orchestration."""

from __future__ import annotations

import time
from typing import Any

import numpy as np

from backend.models.model_manager import MODEL_MANAGER
from backend.pipeline.features import compute_summary_metrics, extract_features
from backend.pipeline.metrics import build_label_image, build_overlay
from backend.pipeline.postprocessing import postprocess_masks
from backend.pipeline.preprocessing import preprocess_from_bgr
from backend.pipeline.segmentation import get_segmentation_model
from backend.utils.image_utils import encode_image_base64, load_image_from_bytes


def run_analysis(content: bytes, filename: str, params: dict[str, Any]) -> dict[str, Any]:
    start = time.perf_counter()
    bgr, display_gray, meta = load_image_from_bytes(content)
    meta["filename"] = filename

    preprocess_params = params.get("preprocessing", {})
    segmentation_params = params.get("segmentation", {})
    postprocess_params = params.get("postprocessing", {})

    preprocess_result = preprocess_from_bgr(bgr, preprocess_params)

    model_name = segmentation_params.get("model", "cellpose")
    if model_name in ("unet", "stardist"):
        raise ValueError(f"{model_name} is not available in this MVP build")

    segmenter = get_segmentation_model(model_name)
    seg_result = segmenter.segment(preprocess_result.preprocessed, segmentation_params)

    post_result = postprocess_masks(seg_result.masks, postprocess_params)
    cells = extract_features(post_result.masks, preprocess_result.preprocessed)
    summary = compute_summary_metrics(cells, preprocess_result.preprocessed.shape)
    elapsed = time.perf_counter() - start

    overlay = build_overlay(preprocess_result.preprocessed, post_result.masks)
    label_img = build_label_image(post_result.masks)

    return {
        "status": "success",
        "mode": "live",
        "processing_time_sec": round(elapsed, 3),
        "image": {
            "filename": filename,
            "width": meta["width"],
            "height": meta["height"],
            "channels": meta["channels"],
            "bit_depth": meta.get("bit_depth", 8),
            "image_type": params.get("image_type", meta.get("image_type", "brightfield")),
        },
        "preprocessing": {
            "steps": preprocess_result.steps,
            "config": preprocess_result.config,
        },
        "segmentation": {
            "model": seg_result.model_name,
            "model_type": seg_result.model_type,
            "metadata": seg_result.metadata,
            "cell_count": int(post_result.masks.max()),
        },
        "postprocessing": {
            "steps": post_result.steps,
            "config": post_result.config,
        },
        "metrics": {
            **summary,
            "processing_time_sec": round(elapsed, 3),
            "image_width": meta["width"],
            "image_height": meta["height"],
        },
        "cells": cells,
        "visualizations": {
            "original": encode_image_base64(display_gray),
            "preprocessed": encode_image_base64(preprocess_result.preprocessed),
            "mask": encode_image_base64((post_result.masks > 0).astype(np.uint8) * 255),
            "overlay": encode_image_base64(overlay),
            "labels": encode_image_base64(label_img),
        },
        "backend": {
            "cellpose_available": MODEL_MANAGER.cellpose_available,
            "cellpose_error": MODEL_MANAGER.cellpose_error,
        },
    }
