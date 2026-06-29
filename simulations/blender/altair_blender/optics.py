"""Optics helpers for educational Blender alignment scenes.

The numerical helpers in this module are intentionally simple geometric teaching
models. They are not a replacement for optical design software.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any

from .prescriptions import LensSurface


VectorTuple = tuple[float, float, float]
Matrix3 = tuple[VectorTuple, ...]


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
    """Raise a clear error when a physical size or scale is not positive.

    Parameters
    ----------
    name
        Name of the value being validated.
    value
        Numeric value that must be finite and positive.
    """

    if not math.isfinite(value) or value <= 0:
        raise ValueError(f"{name} must be positive; got {value!r}")


def spherical_surface_x(surface: LensSurface, *, radial_mm: float) -> float:
    """Return local X coordinate for a spherical surface at radial distance.

    Parameters
    ----------
    surface
        Lens surface to evaluate.
    radial_mm
        Radial distance from the optical axis in millimeters.

    Returns
    -------
    float
        Lens-local X coordinate in millimeters.
    """

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
    """Return the unit normal of a spherical surface at a local Y/Z point.

    Parameters
    ----------
    surface
        Lens surface to evaluate.
    y_mm
        Lens-local Y coordinate in millimeters.
    z_mm
        Lens-local Z coordinate in millimeters.

    Returns
    -------
    Vector3Mm
        Unit normal vector in lens-local coordinates.
    """

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


def _dot(a: VectorTuple, b: VectorTuple) -> float:
    """Return the dot product of two 3D vectors.

    Parameters
    ----------
    a
        First vector.
    b
        Second vector.

    Returns
    -------
    float
        Dot product.
    """

    return (a[0] * b[0]) + (a[1] * b[1]) + (a[2] * b[2])


def _sub(a: VectorTuple, b: VectorTuple) -> VectorTuple:
    """Subtract one 3D vector from another.

    Parameters
    ----------
    a
        Left-hand vector.
    b
        Right-hand vector.

    Returns
    -------
    tuple[float, float, float]
        Difference vector.
    """

    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _add(a: VectorTuple, b: VectorTuple) -> VectorTuple:
    """Add two 3D vectors.

    Parameters
    ----------
    a
        First vector.
    b
        Second vector.

    Returns
    -------
    tuple[float, float, float]
        Sum vector.
    """

    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def _scale(vector: VectorTuple, scalar: float) -> VectorTuple:
    """Scale a 3D vector by a scalar.

    Parameters
    ----------
    vector
        Vector to scale.
    scalar
        Scalar multiplier.

    Returns
    -------
    tuple[float, float, float]
        Scaled vector.
    """

    return (vector[0] * scalar, vector[1] * scalar, vector[2] * scalar)


def _normalize(vector: VectorTuple) -> VectorTuple:
    """Normalize a 3D vector.

    Parameters
    ----------
    vector
        Vector to normalize.

    Returns
    -------
    tuple[float, float, float]
        Unit-length vector.
    """

    length = math.sqrt(_dot(vector, vector))
    validate_positive("vector_length", length)
    return (vector[0] / length, vector[1] / length, vector[2] / length)


def _matmul_vec(matrix: Matrix3, vector: VectorTuple) -> VectorTuple:
    """Multiply a 3x3 matrix by a 3D vector.

    Parameters
    ----------
    matrix
        Matrix rows.
    vector
        Vector to transform.

    Returns
    -------
    tuple[float, float, float]
        Transformed vector.
    """

    return (
        _dot(matrix[0], vector),
        _dot(matrix[1], vector),
        _dot(matrix[2], vector),
    )


def _transpose(matrix: Matrix3) -> Matrix3:
    """Transpose a 3x3 matrix.

    Parameters
    ----------
    matrix
        Matrix rows to transpose.

    Returns
    -------
    tuple[tuple[float, float, float], ...]
        Transposed matrix rows.
    """

    return (
        (matrix[0][0], matrix[1][0], matrix[2][0]),
        (matrix[0][1], matrix[1][1], matrix[2][1]),
        (matrix[0][2], matrix[1][2], matrix[2][2]),
    )


def _rotation_matrix(*, tilt_y_deg: float, tilt_z_deg: float) -> Matrix3:
    """Return a lens-local to world rotation matrix for teaching tilts.

    Parameters
    ----------
    tilt_y_deg
        Y-axis tilt in degrees.
    tilt_z_deg
        Z-axis tilt in degrees.

    Returns
    -------
    tuple[tuple[float, float, float], ...]
        Rotation matrix rows.
    """

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
    """Sample a circular collimated beam bundle.

    Parameters
    ----------
    beam_diameter_mm
        Diameter of the incident beam in millimeters.
    sample_rings
        Number of radial rings to sample around the center ray.

    Returns
    -------
    list[tuple[float, float]]
        Sampled Y/Z offsets in the incident beam.
    """

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
    origin: VectorTuple,
    direction: VectorTuple,
) -> VectorTuple:
    """Intersect a ray with a spherical lens surface.

    Parameters
    ----------
    surface
        Lens surface to intersect.
    origin
        Ray origin in lens-local coordinates.
    direction
        Unit ray direction in lens-local coordinates.

    Returns
    -------
    tuple[float, float, float]
        Nearest valid intersection point.
    """

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
    """Reflect a collimated ray bundle from one spherical surface to the card.

    Parameters
    ----------
    surface
        Lens surface used for the reflection.
    beam_diameter_mm
        Incident beam diameter in millimeters.
    card_to_lens_mm
        Distance from the aperture card to the lens center in millimeters.
    tilt_y_deg
        Lens tilt around the Z axis, expressed as horizontal beam walk.
    tilt_z_deg
        Lens tilt around the Y axis, expressed as vertical beam walk.
    decenter_y_mm
        Lens decenter in the Y direction.
    decenter_z_mm
        Lens decenter in the Z direction.
    sample_rings
        Number of radial rings used to sample the incident beam bundle.

    Returns
    -------
    ReflectedSpotSummary
        Center, footprint, and sampled return points on the aperture card.
    """

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

    Parameters
    ----------
    tilt_y_deg
        Lens tilt driving horizontal spot displacement.
    tilt_z_deg
        Lens tilt driving vertical spot displacement.
    decenter_y_mm
        Lens decenter in the Y direction.
    decenter_z_mm
        Lens decenter in the Z direction.
    card_to_lens_mm
        Distance from card to lens in millimeters.
    exaggeration
        Visual exaggeration factor for display offsets.
    decenter_response
        Relative strength of decenter-induced spot splitting.

    Returns
    -------
    tuple[SpotOffset, SpotOffset]
        Teaching-level offsets for two return spots.
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
    material: Any,
    collection: Any,
) -> Any:
    """Create a glowing cylindrical beam between two scene points.

    Parameters
    ----------
    name
        Beam object name.
    start_xyz
        Beam start point in scene coordinates.
    end_xyz
        Beam end point in scene coordinates.
    radius_mm
        Beam cylinder radius in millimeters.
    material
        Blender material assigned to the beam.
    collection
        Blender collection that should contain the beam.

    Returns
    -------
    object
        Blender mesh object for the beam.
    """

    from mathutils import Vector  # pyright: ignore[reportMissingImports]

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
    material: Any,
    collection: Any,
    optical_axis_z_mm: float = 15.0,
) -> Any:
    """Create a small return spot on the card face.

    Parameters
    ----------
    name
        Spot object name.
    card_x_mm
        Aperture card X position in millimeters.
    offset
        Spot offset on the aperture card.
    radius_mm
        Spot radius in millimeters.
    material
        Blender material assigned to the spot.
    collection
        Blender collection that should contain the spot.
    optical_axis_z_mm
        Optical-axis height in millimeters.

    Returns
    -------
    object
        Blender mesh object for the spot.
    """

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
