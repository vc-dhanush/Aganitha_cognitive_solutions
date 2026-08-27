"""Generate synthetic brightfield sample and demo analysis JSON."""

from __future__ import annotations

import json
import os
import time

import cv2
import numpy as np

from backend.pipeline.features import compute_summary_metrics, extract_features
from backend.pipeline.metrics import build_label_image, build_overlay
from backend.pipeline.postprocessing import postprocess_masks
from backend.pipeline.preprocessing import preprocess_from_bgr
from backend.utils.image_utils import encode_image_base64, normalize_to_uint8


def create_sample_image(path: str, size: int = 512) -> tuple[np.ndarray, list[tuple[int, int, int]]]:
    rng = np.random.default_rng(42)
    base = np.full((size, size), 200, dtype=np.uint8)
    circles: list[tuple[int, int, int]] = []
    attempts = 0
    while len(circles) < 28 and attempts < 500:
        attempts += 1
        cx = rng.integers(45, size - 45)
        cy = rng.integers(45, size - 45)
        radius = rng.integers(12, 20)
        overlap = False
        for px, py, pr in circles:
            if np.hypot(cx - px, cy - py) < (radius + pr + 6):
                overlap = True
                break
        if overlap:
            continue
        intensity = int(rng.integers(70, 120))
        cv2.circle(base, (cx, cy), radius, intensity, -1)
        circles.append((cx, cy, radius))
    noise = rng.normal(0, 6, base.shape).astype(np.int16)
    image = np.clip(base.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    cv2.imwrite(path, image)
    return image, circles


def masks_from_circles(shape: tuple[int, int], circles: list[tuple[int, int, int]]) -> np.ndarray:
    masks = np.zeros(shape, dtype=np.int32)
    for idx, (cx, cy, radius) in enumerate(circles, start=1):
        cv2.circle(masks, (cx, cy), radius, idx, -1)
    return masks


def build_demo_result(content: bytes, filename: str, circles: list[tuple[int, int, int]]) -> dict:
    start = time.perf_counter()
    arr = cv2.imdecode(np.frombuffer(content, np.uint8), cv2.IMREAD_GRAYSCALE)
    bgr = cv2.cvtColor(arr, cv2.COLOR_GRAY2BGR)
    height, width = arr.shape

    preprocess_result = preprocess_from_bgr(
        bgr,
        {
            "illumination_correction": True,
            "denoise": True,
            "normalize_contrast": True,
        },
    )

    raw_masks = masks_from_circles(arr.shape, circles)
    post_result = postprocess_masks(
        raw_masks,
        {
            "enabled": True,
            "min_area": 80,
            "max_area": 50000,
            "remove_border": True,
            "fill_holes": True,
            "morph_cleanup": True,
        },
    )
    cells = extract_features(post_result.masks, preprocess_result.preprocessed)
    summary = compute_summary_metrics(cells, preprocess_result.preprocessed.shape)
    elapsed = time.perf_counter() - start

    overlay = build_overlay(preprocess_result.preprocessed, post_result.masks)
    label_img = build_label_image(post_result.masks)

    return {
        "status": "success",
        "mode": "demo",
        "processing_time_sec": round(elapsed, 3),
        "image": {
            "filename": filename,
            "width": width,
            "height": height,
            "channels": 1,
            "bit_depth": 8,
            "image_type": "brightfield",
        },
        "preprocessing": {
            "steps": preprocess_result.steps,
            "config": preprocess_result.config,
        },
        "segmentation": {
            "model": "synthetic_ground_truth",
            "model_type": "brightfield_synthetic",
            "metadata": {"backend": "demo_generator", "note": "Precomputed from synthetic ground-truth masks"},
            "cell_count": int(post_result.masks.max()),
        },
        "postprocessing": {
            "steps": post_result.steps,
            "config": post_result.config,
        },
        "metrics": {
            **summary,
            "processing_time_sec": round(elapsed, 3),
            "image_width": width,
            "image_height": height,
        },
        "cells": cells,
        "visualizations": {
            "original": encode_image_base64(normalize_to_uint8(arr)),
            "preprocessed": encode_image_base64(preprocess_result.preprocessed),
            "mask": encode_image_base64((post_result.masks > 0).astype(np.uint8) * 255),
            "overlay": encode_image_base64(overlay),
            "labels": encode_image_base64(label_img),
        },
        "backend": {
            "cellpose_available": False,
            "cellpose_error": "Demo assets generated without Cellpose",
        },
    }


def main() -> None:
    root = os.path.join(os.path.dirname(__file__), "..", "samples")
    os.makedirs(root, exist_ok=True)
    sample_path = os.path.join(root, "sample_cells.png")
    image, circles = create_sample_image(sample_path)

    with open(sample_path, "rb") as handle:
        content = handle.read()

    result = build_demo_result(content, "sample_cells.png", circles)

    demo_path = os.path.join(root, "demo_result.json")
    with open(demo_path, "w", encoding="utf-8") as handle:
        json.dump(result, handle)

    frontend_public = os.path.join(
        os.path.dirname(__file__), "..", "..", "frontend", "public", "demo"
    )
    os.makedirs(frontend_public, exist_ok=True)
    with open(os.path.join(frontend_public, "demo_result.json"), "w", encoding="utf-8") as handle:
        json.dump(result, handle)

    frontend_samples = os.path.join(
        os.path.dirname(__file__), "..", "..", "frontend", "public", "samples"
    )
    os.makedirs(frontend_samples, exist_ok=True)
    cv2.imwrite(os.path.join(frontend_samples, "sample_cells.png"), image)

    print(f"Created {sample_path}")
    print(f"Created {demo_path}")
    print(f"Cells detected: {result['metrics']['cell_count']}")


if __name__ == "__main__":
    main()
