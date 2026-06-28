"""Optics helpers for educational Blender alignment scenes.

The numerical helpers in this module are intentionally simple geometric teaching
models. They are not a replacement for optical design software.
"""

from __future__ import annotations

from dataclasses import dataclass
import math

from .prescriptions import LensSurface


@dataclass(frozen=True)
class SpotOffset:
    """Return-spot offset on the business card face, in millimeters."""

    y_mm: float
    z_mm: float


@dataclass(frozen=True)
class Vector3Mm:
    """Small 3D vector helper for import-safe geometric calculations."""

    x_mm: float
    y_mm: float
    z_mm: float


@dataclass(frozen=True)
class ReflectedSpotSummary:
    """Center and footprint of one reflected ray bundle on the card."""

    surface_name: str
    center: SpotOffset
    diameter_mm: float
    reflected_points: tuple[SpotOffset, ...]


def validate_positive(name: str, value: float) -> None:
    """Raise a clear error when a physical size or scale is not positive."""

    if not math.isfinite(value) or value <= 0:
        raise ValueError(f"{name} must be positive; got {value!r}")


def spherical_surface_x(surface: LensSurface, *, radial_mm: float) -> float:
    """Return local X coordinate for a spherical surface at radial distance."""

    if radial_mm < 0 or radial_mm > surface.clear_radius_mm:
        raise ValueError(
            f"radial_mm must be within the clear aperture; got {radial_mm!r}"
        )

    radius_abs = abs(surface.radius_mm)
    if radial_mm >= radius_abs:
        raise ValueError("radial_mm must be smaller than the surface radius")

    root = math.sqrt((radius_abs * radius_abs) - (radial_mm * radial_mm))
    sign = 1.0 if surface.radius_mm > 0.0 else -1.0
    return surface.vertex_x_mm + surface.radius_mm - (sign * root)


def spherical_surface_normal(
    surface: LensSurface, *, y_mm: float, z_mm: float
) -> Vector3Mm:
    """Return the unit normal of a spherical surface at a local Y/Z point."""

    radial_mm = math.hypot(y_mm, z_mm)
    point_x = spherical_surface_x(surface, radial_mm=radial_mm)
    center_x = surface.vertex_x_mm + surface.radius_mm
    vector = (point_x - center_x, y_mm, z_mm)
    length = math.sqrt(sum(component * component for component in vector))
    validate_positive("normal_length", length)
    return Vector3Mm(
        x_mm=vector[0] / length,
        y_mm=vector[1] / length,
        z_mm=vector[2] / length,
    )


def _dot(a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
    return (a[0] * b[0]) + (a[1] * b[1]) + (a[2] * b[2])


def _sub(
    a: tuple[float, float, float], b: tuple[float, float, float]
) -> tuple[float, float, float]:
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _add(
    a: tuple[float, float, float], b: tuple[float, float, float]
) -> tuple[float, float, float]:
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def _scale(
    vector: tuple[float, float, float], scalar: float
) -> tuple[float, float, float]:
    return (vector[0] * scalar, vector[1] * scalar, vector[2] * scalar)


def _normalize(vector: tuple[float, float, float]) -> tuple[float, float, float]:
    length = math.sqrt(_dot(vector, vector))
    validate_positive("vector_length", length)
    return (vector[0] / length, vector[1] / length, vector[2] / length)


def _matmul_vec(
    matrix: tuple[tuple[float, float, float], ...], vector: tuple[float, float, float]
) -> tuple[float, float, float]:
    return (
        _dot(matrix[0], vector),
        _dot(matrix[1], vector),
        _dot(matrix[2], vector),
    )


def _transpose(
    matrix: tuple[tuple[float, float, float], ...],
) -> tuple[tuple[float, float, float], ...]:
    return (
        (matrix[0][0], matrix[1][0], matrix[2][0]),
        (matrix[0][1], matrix[1][1], matrix[2][1]),
        (matrix[0][2], matrix[1][2], matrix[2][2]),
    )


def _rotation_matrix(
    *, tilt_y_deg: float, tilt_z_deg: float
) -> tuple[tuple[float, float, float], ...]:
    """Return a lens-local to world rotation matrix for teaching tilts."""

    yaw = math.radians(tilt_y_deg)
    pitch = math.radians(-tilt_z_deg)
    cy = math.cos(yaw)
    sy = math.sin(yaw)
    cp = math.cos(pitch)
    sp = math.sin(pitch)

    rz = ((cy, -sy, 0.0), (sy, cy, 0.0), (0.0, 0.0, 1.0))
    ry = ((cp, 0.0, sp), (0.0, 1.0, 0.0), (-sp, 0.0, cp))
    return (
        (
            (rz[0][0] * ry[0][0]) + (rz[0][1] * ry[1][0]),
            (rz[0][0] * ry[0][1]) + (rz[0][1] * ry[1][1]),
            (rz[0][0] * ry[0][2]) + (rz[0][1] * ry[1][2]),
        ),
        (
            (rz[1][0] * ry[0][0]) + (rz[1][1] * ry[1][0]),
            (rz[1][0] * ry[0][1]) + (rz[1][1] * ry[1][1]),
            (rz[1][0] * ry[0][2]) + (rz[1][1] * ry[1][2]),
        ),
        (
            (rz[2][0] * ry[0][0]) + (rz[2][2] * ry[2][0]),
            (rz[2][0] * ry[0][1]) + (rz[2][2] * ry[2][1]),
            (rz[2][0] * ry[0][2]) + (rz[2][2] * ry[2][2]),
        ),
    )


def _sample_bundle(
    beam_diameter_mm: float, sample_rings: int
) -> list[tuple[float, float]]:
    validate_positive("beam_diameter_mm", beam_diameter_mm)
    if sample_rings < 1:
        raise ValueError("sample_rings must be at least 1")

    radius = beam_diameter_mm / 2.0
    samples = [(0.0, 0.0)]
    for ring in range(1, sample_rings + 1):
        ring_radius = radius * (ring / sample_rings)
        count = 8 * ring
        for index in range(count):
            angle = (2.0 * math.pi * index) / count
            samples.append(
                (ring_radius * math.cos(angle), ring_radius * math.sin(angle))
            )
    return samples


def _intersect_spherical_surface(
    *,
    surface: LensSurface,
    origin: tuple[float, float, float],
    direction: tuple[float, float, float],
) -> tuple[float, float, float]:
    center = (surface.vertex_x_mm + surface.radius_mm, 0.0, 0.0)
    oc = _sub(origin, center)
    a = _dot(direction, direction)
    b = 2.0 * _dot(oc, direction)
    c = _dot(oc, oc) - (abs(surface.radius_mm) ** 2)
    discriminant = (b * b) - (4.0 * a * c)
    if discriminant < 0.0:
        raise ValueError(f"ray does not intersect surface {surface.name}")

    root = math.sqrt(discriminant)
    candidates = [(-b - root) / (2.0 * a), (-b + root) / (2.0 * a)]
    points: list[tuple[float, float, float]] = []
    for candidate in candidates:
        if candidate <= 1e-9:
            continue
        point = _add(origin, _scale(direction, candidate))
        if math.hypot(point[1], point[2]) <= surface.clear_radius_mm:
            points.append(point)
    if not points:
        raise ValueError(f"ray misses clear aperture on surface {surface.name}")
    return min(points, key=lambda point: point[0])


def reflect_ray_bundle_from_surface(
    *,
    surface: LensSurface,
    beam_diameter_mm: float,
    card_to_lens_mm: float,
    tilt_y_deg: float,
    tilt_z_deg: float,
    decenter_y_mm: float,
    decenter_z_mm: float,
    sample_rings: int = 3,
) -> ReflectedSpotSummary:
    """Reflect a collimated ray bundle from one spherical surface to the card."""

    validate_positive("card_to_lens_mm", card_to_lens_mm)

    rotation = _rotation_matrix(tilt_y_deg=tilt_y_deg, tilt_z_deg=tilt_z_deg)
    inverse_rotation = _transpose(rotation)
    lens_center_world = (0.0, decenter_y_mm, decenter_z_mm)
    card_x_world = -card_to_lens_mm
    incoming_direction_world = (1.0, 0.0, 0.0)
    incoming_direction_local = _normalize(
        _matmul_vec(inverse_rotation, incoming_direction_world)
    )

    reflected_points: list[SpotOffset] = []
    for sample_y, sample_z in _sample_bundle(beam_diameter_mm, sample_rings):
        origin_world = (card_x_world, sample_y, sample_z)
        origin_local = _matmul_vec(
            inverse_rotation, _sub(origin_world, lens_center_world)
        )
        hit_local = _intersect_spherical_surface(
            surface=surface,
            origin=origin_local,
            direction=incoming_direction_local,
        )
        normal = spherical_surface_normal(surface, y_mm=hit_local[1], z_mm=hit_local[2])
        normal_tuple = (normal.x_mm, normal.y_mm, normal.z_mm)
        reflected_direction_local = _normalize(
            _sub(
                incoming_direction_local,
                _scale(
                    normal_tuple, 2.0 * _dot(incoming_direction_local, normal_tuple)
                ),
            )
        )
        hit_world = _add(_matmul_vec(rotation, hit_local), lens_center_world)
        reflected_direction_world = _normalize(
            _matmul_vec(rotation, reflected_direction_local)
        )
        card_t = (card_x_world - hit_world[0]) / reflected_direction_world[0]
        card_point = _add(hit_world, _scale(reflected_direction_world, card_t))
        reflected_points.append(SpotOffset(y_mm=card_point[1], z_mm=card_point[2]))

    center_y = sum(point.y_mm for point in reflected_points) / len(reflected_points)
    center_z = sum(point.z_mm for point in reflected_points) / len(reflected_points)
    center = SpotOffset(y_mm=center_y, z_mm=center_z)
    radius = max(
        math.hypot(point.y_mm - center_y, point.z_mm - center_z)
        for point in reflected_points
    )
    return ReflectedSpotSummary(
        surface_name=surface.name,
        center=center,
        diameter_mm=2.0 * radius,
        reflected_points=tuple(reflected_points),
    )


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
    optical_axis_z_mm: float = 15.0,
):
    """Create a small return spot on the card face."""

    from .scene import get_bpy

    validate_positive("radius_mm", radius_mm)
    bpy = get_bpy()
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=32,
        ring_count=16,
        radius=radius_mm,
        location=(card_x_mm - 0.9, offset.y_mm, optical_axis_z_mm + offset.z_mm),
    )
    spot = bpy.context.object
    spot.name = name
    spot.scale.x = 0.18
    spot.data.materials.append(material)
    for existing in spot.users_collection:
        existing.objects.unlink(spot)
    collection.objects.link(spot)
    return spot
