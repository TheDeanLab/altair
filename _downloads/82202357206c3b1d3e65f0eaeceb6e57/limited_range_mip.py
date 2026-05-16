#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "numpy>=1.23",
#     "tifffile>=2023.7.10",
# ]
# ///
"""Create limited-z maximum-intensity projections from 3D TIFF stacks.

The script expects TIFF stacks in Z, Y, X axis order. It writes XY, XZ, YZ,
and combined-view projections for each input file.
"""

from __future__ import annotations

import argparse
import glob
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Sequence

import numpy as np
import tifffile

BIGTIFF_THRESHOLD_BYTES = 4 * 1024**3


@dataclass(frozen=True)
class Roi:
    """ImageJ/Fiji-style ROI coordinates."""

    x: int
    y: int
    width: int
    height: int


@dataclass(frozen=True)
class ZRange:
    """One-based inclusive z range."""

    first: int
    last: int


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Create limited-z maximum-intensity projections from one or more "
            "3D TIFF stacks. Z indices are one-based and inclusive, matching "
            "the slice labels shown in Fiji/ImageJ."
        )
    )
    parser.add_argument(
        "inputs",
        nargs="+",
        help=(
            "Input TIFF stack path(s). Quoted glob patterns such as "
            "'/data/Cell10/1_CH0*.tif' are expanded by this script."
        ),
    )
    parser.add_argument(
        "--first-z",
        type=int,
        required=True,
        help="First z slice to include, using one-based inclusive indexing.",
    )
    parser.add_argument(
        "--last-z",
        type=int,
        required=True,
        help="Last z slice to include, using one-based inclusive indexing.",
    )
    parser.add_argument(
        "--roi",
        type=int,
        nargs=4,
        metavar=("X", "Y", "WIDTH", "HEIGHT"),
        help=(
            "Optional ImageJ/Fiji-style XY crop in pixels. X and Y are the "
            "upper-left corner coordinates, and WIDTH/HEIGHT are crop sizes."
        ),
    )
    parser.add_argument(
        "--xy-pixel-size",
        type=float,
        help=(
            "Optional lateral pixel size. Provide with --z-step-size to scale "
            "XZ/YZ projections so the displayed z axis has the same physical "
            "pixel spacing as X/Y."
        ),
    )
    parser.add_argument(
        "--z-step-size",
        type=float,
        help="Optional z-step size in the same units as --xy-pixel-size.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Directory for outputs. Defaults to a MIPs folder beside each input.",
    )
    parser.add_argument(
        "--suffix",
        help=(
            "Optional output suffix. Defaults to z<first>-<last>, for example "
            "z0451-0640."
        ),
    )
    parser.add_argument(
        "--write-cropped-stack",
        action="store_true",
        help="Also write the cropped limited-z stack for each input.",
    )
    parser.add_argument(
        "--no-montage",
        action="store_true",
        help="Skip the combined XY/XZ/YZ projection image.",
    )
    return parser.parse_args()


def expand_inputs(patterns: Sequence[str]) -> list[Path]:
    paths: list[Path] = []
    for pattern in patterns:
        matches = sorted(glob.glob(pattern))
        if matches:
            paths.extend(Path(match) for match in matches)
        else:
            paths.append(Path(pattern))

    missing = [path for path in paths if not path.exists()]
    if missing:
        missing_text = "\n".join(str(path) for path in missing)
        raise FileNotFoundError(f"Input TIFF file(s) not found:\n{missing_text}")

    return paths


def validate_z_range(z_range: ZRange, z_len: int) -> slice:
    if z_range.first < 1:
        raise ValueError("--first-z must be at least 1")
    if z_range.last < z_range.first:
        raise ValueError("--last-z must be greater than or equal to --first-z")
    if z_range.last > z_len:
        raise ValueError(
            f"Requested z range {z_range.first}-{z_range.last}, "
            f"but stack only has {z_len} slices"
        )

    return slice(z_range.first - 1, z_range.last)


def validate_roi(roi: Roi, y_len: int, x_len: int) -> tuple[slice, slice]:
    if roi.x < 0 or roi.y < 0:
        raise ValueError("ROI X and Y must be non-negative")
    if roi.width < 1 or roi.height < 1:
        raise ValueError("ROI WIDTH and HEIGHT must be at least 1")

    x_stop = roi.x + roi.width
    y_stop = roi.y + roi.height
    if x_stop > x_len or y_stop > y_len:
        raise ValueError(
            f"ROI x={roi.x}, y={roi.y}, width={roi.width}, height={roi.height} "
            f"exceeds image size X={x_len}, Y={y_len}"
        )

    return slice(roi.y, y_stop), slice(roi.x, x_stop)


def cast_like(values: np.ndarray, dtype: np.dtype) -> np.ndarray:
    if np.issubdtype(dtype, np.integer):
        info = np.iinfo(dtype)
        values = np.clip(np.rint(values), info.min, info.max)
    return values.astype(dtype, copy=False)


def rescale_z_axis(image: np.ndarray, scale: float, dtype: np.dtype) -> np.ndarray:
    if scale <= 0:
        raise ValueError("Projection scale must be positive")
    if abs(scale - 1.0) < 1e-9:
        return image

    old_rows = image.shape[0]
    new_rows = max(1, int(round(old_rows * scale)))
    if new_rows == old_rows:
        return image

    old_positions = np.arange(old_rows, dtype=np.float64)
    new_positions = np.linspace(0, old_rows - 1, new_rows)
    flat_image = image.reshape(old_rows, -1).astype(np.float64, copy=False)
    flat_scaled = np.empty((new_rows, flat_image.shape[1]), dtype=np.float64)

    for column in range(flat_image.shape[1]):
        flat_scaled[:, column] = np.interp(
            new_positions,
            old_positions,
            flat_image[:, column],
        )

    scaled = flat_scaled.reshape((new_rows, *image.shape[1:]))
    return cast_like(scaled, dtype)


def projection_scale(
    xy_pixel_size: Optional[float],
    z_step_size: Optional[float],
) -> float:
    if xy_pixel_size is None and z_step_size is None:
        return 1.0
    if xy_pixel_size is None or z_step_size is None:
        raise ValueError("Provide both --xy-pixel-size and --z-step-size, or neither")
    if xy_pixel_size <= 0 or z_step_size <= 0:
        raise ValueError("--xy-pixel-size and --z-step-size must be positive")
    return z_step_size / xy_pixel_size


def write_tiff(path: Path, image: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tifffile.imwrite(
        path,
        image,
        bigtiff=image.nbytes > BIGTIFF_THRESHOLD_BYTES,
        photometric="minisblack",
    )


def create_montage(
    xy: np.ndarray,
    xz: np.ndarray,
    yz: np.ndarray,
    dtype: np.dtype,
) -> np.ndarray:
    height = xy.shape[0] + xz.shape[0]
    width = xy.shape[1] + yz.shape[1]
    montage = np.zeros((height, width), dtype=dtype)
    montage[: xy.shape[0], : xy.shape[1]] = xy
    montage[xy.shape[0] :, : xz.shape[1]] = xz
    montage[: yz.shape[0], xy.shape[1] :] = yz
    return montage


def process_stack(
    input_path: Path,
    output_dir: Path,
    z_range: ZRange,
    roi: Optional[Roi],
    scale: float,
    suffix: str,
    write_cropped_stack: bool,
    write_montage: bool,
) -> list[Path]:
    stack = tifffile.imread(input_path)
    if stack.ndim != 3:
        raise ValueError(
            f"{input_path} has shape {stack.shape}; expected a 3D TIFF stack "
            "in Z, Y, X axis order"
        )

    z_slice = validate_z_range(z_range, stack.shape[0])
    stack = stack[z_slice, :, :]

    if roi is not None:
        y_slice, x_slice = validate_roi(roi, stack.shape[1], stack.shape[2])
        stack = stack[:, y_slice, x_slice]

    xy = stack.max(axis=0)
    xz = rescale_z_axis(stack.max(axis=1), scale, stack.dtype)
    yz = rescale_z_axis(stack.max(axis=2), scale, stack.dtype).T

    output_paths: list[Path] = []
    stem = input_path.stem
    projections = {
        "xy": xy,
        "xz": xz,
        "yz": yz,
    }
    if write_montage:
        projections["three"] = create_montage(xy, xz, yz, stack.dtype)

    for name, image in projections.items():
        output_path = output_dir / f"{stem}_{suffix}_mip_{name}.tif"
        write_tiff(output_path, image)
        output_paths.append(output_path)

    if write_cropped_stack:
        output_path = output_dir / f"{stem}_{suffix}_stack.tif"
        write_tiff(output_path, stack)
        output_paths.append(output_path)

    return output_paths


def main() -> None:
    args = parse_args()
    paths = expand_inputs(args.inputs)
    z_range = ZRange(args.first_z, args.last_z)
    roi = Roi(*args.roi) if args.roi is not None else None
    scale = projection_scale(args.xy_pixel_size, args.z_step_size)
    suffix = args.suffix or f"z{args.first_z:04d}-{args.last_z:04d}"

    for input_path in paths:
        output_dir = args.output_dir or input_path.parent / "MIPs"
        output_paths = process_stack(
            input_path=input_path,
            output_dir=output_dir,
            z_range=z_range,
            roi=roi,
            scale=scale,
            suffix=suffix,
            write_cropped_stack=args.write_cropped_stack,
            write_montage=not args.no_montage,
        )
        for output_path in output_paths:
            print(f"Saved {output_path}")


if __name__ == "__main__":
    main()
