"""Optics helpers for educational Blender alignment scenes.

The numerical helpers in this module are intentionally simple geometric teaching
models. They are not a replacement for optical design software.
"""

from __future__ import annotations

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class SpotOffset:
    """Return-spot offset on the business card face, in millimeters."""

    y_mm: float
    z_mm: float


def validate_positive(name: str, value: float) -> None:
    """Raise a clear error when a physical size or scale is not positive."""

    if not math.isfinite(value) or value <= 0:
        raise ValueError(f"{name} must be positive; got {value!r}")


def compute_return_spots(
    *,
    tilt_y_deg: float,
    tilt_z_deg: float,
    decenter_y_mm: float,
    decenter_z_mm: float,
    card_to_lens_mm: float,
    exaggeration: float,
    decenter_response: float = 1.0,
) -> tuple[SpotOffset, SpotOffset]:
    """Compute teaching-level return-spot offsets for two lens reflections.

    A lens tilt creates a common walk-off of both reflected spots. A lens
    decenter splits the two surface reflections in opposite directions. The two
    surfaces are given slightly different tilt sensitivity so the viewer can
    distinguish the two return spots during correction.
    """

    validate_positive("card_to_lens_mm", card_to_lens_mm)
    validate_positive("exaggeration", exaggeration)
    validate_positive("decenter_response", decenter_response)

    common_y = 2.0 * math.tan(math.radians(tilt_y_deg)) * card_to_lens_mm * exaggeration
    common_z = 2.0 * math.tan(math.radians(tilt_z_deg)) * card_to_lens_mm * exaggeration
    split_y = decenter_y_mm * decenter_response * exaggeration
    split_z = decenter_z_mm * decenter_response * exaggeration

    spot_a = SpotOffset(
        y_mm=(0.85 * common_y) + split_y,
        z_mm=(0.85 * common_z) + split_z,
    )
    spot_b = SpotOffset(
        y_mm=(1.15 * common_y) - split_y,
        z_mm=(1.15 * common_z) - split_z,
    )
    return spot_a, spot_b


def create_beam_between(
    *,
    name: str,
    start_xyz: tuple[float, float, float],
    end_xyz: tuple[float, float, float],
    radius_mm: float,
    material,
    collection,
):
    """Create a glowing cylindrical beam between two scene points."""

    from mathutils import Vector  # type: ignore[import-not-found]

    from .scene import get_bpy

    validate_positive("radius_mm", radius_mm)
    bpy = get_bpy()
    start = Vector(start_xyz)
    end = Vector(end_xyz)
    direction = end - start
    length = direction.length
    validate_positive("beam_length", length)

    midpoint = start + (direction * 0.5)
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=32, radius=radius_mm, depth=length, location=midpoint
    )
    beam = bpy.context.object
    beam.name = name
    beam.rotation_euler = direction.to_track_quat("Z", "Y").to_euler()
    beam.data.materials.append(material)
    for existing in beam.users_collection:
        existing.objects.unlink(beam)
    collection.objects.link(beam)
    return beam


def create_return_spot(
    *,
    name: str,
    card_x_mm: float,
    offset: SpotOffset,
    radius_mm: float,
    material,
    collection,
):
    """Create a small return spot on the card face."""

    from .scene import get_bpy

    validate_positive("radius_mm", radius_mm)
    bpy = get_bpy()
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=32,
        ring_count=16,
        radius=radius_mm,
        location=(card_x_mm - 0.9, offset.y_mm, 15.0 + offset.z_mm),
    )
    spot = bpy.context.object
    spot.name = name
    spot.scale.x = 0.18
    spot.data.materials.append(material)
    for existing in spot.users_collection:
        existing.objects.unlink(spot)
    collection.objects.link(spot)
    return spot
