"""Visualization helpers for masks and overlays."""

from __future__ import annotations

import numpy as np
from skimage.color import label2rgb


def build_overlay(original: np.ndarray, masks: np.ndarray, alpha: float = 0.45) -> np.ndarray:
    if original.ndim == 2:
        base = np.stack([original, original, original], axis=-1)
    else:
        base = original.copy()
    if masks.max() == 0:
        return base
    colored = label2rgb(masks, image=base, bg_label=0, alpha=alpha, image_alpha=1.0)
    return (colored * 255).astype(np.uint8)


def build_label_image(masks: np.ndarray) -> np.ndarray:
    if masks.max() == 0:
        return np.zeros_like(masks, dtype=np.uint8)
    normalized = (masks.astype(np.float32) / masks.max()) * 255
    return normalized.astype(np.uint8)
