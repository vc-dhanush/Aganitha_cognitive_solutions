"""Microscopy image preprocessing pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import cv2
import numpy as np
from skimage import exposure, restoration
from skimage.morphology import disk, opening, white_tophat

from backend.utils.image_utils import normalize_to_uint8, to_grayscale


@dataclass
class PreprocessConfig:
    illumination_correction: bool = True
    illumination_method: str = "background_subtraction"
    background_radius: int = 50
    denoise: bool = True
    denoise_method: str = "gaussian"
    normalize_contrast: bool = True


@dataclass
class PreprocessResult:
    original: np.ndarray
    preprocessed: np.ndarray
    steps: list[str] = field(default_factory=list)
    config: dict[str, Any] = field(default_factory=dict)


def preprocess_image(gray: np.ndarray, config: PreprocessConfig) -> PreprocessResult:
    original = gray.copy()
    working = normalize_to_uint8(gray)
    steps: list[str] = ["normalize_dtype"]

    if config.illumination_correction:
        working = apply_illumination_correction(
            working, config.illumination_method, config.background_radius
        )
        steps.append(f"illumination_{config.illumination_method}")

    if config.denoise:
        working = apply_denoising(working, config.denoise_method)
        steps.append(f"denoise_{config.denoise_method}")

    if config.normalize_contrast:
        working = exposure.equalize_adapthist(working, clip_limit=0.03)
        working = (working * 255).astype(np.uint8)
        steps.append("contrast_normalization")

    return PreprocessResult(
        original=original,
        preprocessed=working,
        steps=steps,
        config={
            "illumination_correction": config.illumination_correction,
            "illumination_method": config.illumination_method,
            "background_radius": config.background_radius,
            "denoise": config.denoise,
            "denoise_method": config.denoise_method,
            "normalize_contrast": config.normalize_contrast,
        },
    )


def apply_illumination_correction(
    image: np.ndarray, method: str, radius: int
) -> np.ndarray:
    radius = max(5, min(radius, 200))
    if method == "morphological_correction":
        selem = disk(radius)
        background = opening(image, selem)
        corrected = cv2.subtract(image, background)
        return normalize_to_uint8(corrected)
    selem = disk(radius)
    background = white_tophat(image, selem)
    corrected = cv2.subtract(image, background)
    return normalize_to_uint8(corrected)


def apply_denoising(image: np.ndarray, method: str) -> np.ndarray:
    if method == "median":
        return cv2.medianBlur(image, 5)
    if method == "non_local_means":
        return cv2.fastNlMeansDenoising(image, None, 10, 7, 21)
    return cv2.GaussianBlur(image, (5, 5), 0)


def preprocess_from_bgr(bgr: np.ndarray, params: dict[str, Any]) -> PreprocessResult:
    gray = to_grayscale(bgr)
    config = PreprocessConfig(
        illumination_correction=bool(params.get("illumination_correction", True)),
        illumination_method=params.get("illumination_method", "background_subtraction"),
        background_radius=int(params.get("background_radius", 50)),
        denoise=bool(params.get("denoise", True)),
        denoise_method=params.get("denoise_method", "gaussian"),
        normalize_contrast=bool(params.get("normalize_contrast", True)),
    )
    return preprocess_image(gray, config)
