"""Mask cleanup and morphological post-processing."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
from skimage.morphology import binary_closing, binary_opening, disk, remove_small_objects
from skimage.segmentation import clear_border

from backend.pipeline.features import relabel_sequential


@dataclass
class PostprocessResult:
    masks: np.ndarray
    steps: list[str] = field(default_factory=list)
    config: dict[str, Any] = field(default_factory=dict)


def postprocess_masks(masks: np.ndarray, params: dict[str, Any]) -> PostprocessResult:
    if not params.get("enabled", True):
        return PostprocessResult(masks=masks, steps=["skipped"], config=params)

    min_area = int(params.get("min_area", 50))
    max_area = int(params.get("max_area", 50000))
    remove_border = bool(params.get("remove_border", True))
    fill_holes = bool(params.get("fill_holes", True))
    morph_cleanup = bool(params.get("morph_cleanup", True))

    steps: list[str] = []
    working = masks.astype(np.int32)

    if remove_border:
        binary = working > 0
        cleared = clear_border(binary)
        working = relabel_from_binary(cleared, working)
        steps.append("remove_border")

    if fill_holes or morph_cleanup:
        unique_ids = np.unique(working)
        unique_ids = unique_ids[unique_ids != 0]
        cleaned = np.zeros_like(working)
        selem = disk(2)
        for cell_id in unique_ids:
            cell_mask = working == cell_id
            if fill_holes:
                from scipy import ndimage as ndi

                cell_mask = ndi.binary_fill_holes(cell_mask)
            if morph_cleanup:
                cell_mask = binary_opening(cell_mask, selem)
                cell_mask = binary_closing(cell_mask, selem)
            cleaned[cell_mask] = cell_id
        working = cleaned
        if fill_holes:
            steps.append("fill_holes")
        if morph_cleanup:
            steps.append("morph_cleanup")

    filtered = np.zeros_like(working)
    new_id = 1
    for cell_id in np.unique(working):
        if cell_id == 0:
            continue
        cell_mask = working == cell_id
        area = int(cell_mask.sum())
        if area < min_area or area > max_area:
            continue
        filtered[cell_mask] = new_id
        new_id += 1
    steps.append("area_filter")

    filtered = relabel_sequential(filtered)
    return PostprocessResult(
        masks=filtered,
        steps=steps,
        config={
            "enabled": True,
            "min_area": min_area,
            "max_area": max_area,
            "remove_border": remove_border,
            "fill_holes": fill_holes,
            "morph_cleanup": morph_cleanup,
        },
    )


def relabel_from_binary(binary: np.ndarray, original: np.ndarray) -> np.ndarray:
    output = np.zeros_like(original)
    new_id = 1
    for old_id in np.unique(original):
        if old_id == 0:
            continue
        mask = (original == old_id) & binary
        if mask.any():
            output[mask] = new_id
            new_id += 1
    return output
