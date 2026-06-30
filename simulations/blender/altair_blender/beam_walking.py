"""Import-safe model for walking a laser beam through two irises."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
import math

VectorTuple = tuple[float, float, float]


@dataclass(frozen=True)
class IrisOffset:
    """Transverse beam offset at one iris."""

    y_mm: float
    z_mm: float


@dataclass(frozen=True)
class BeamIntercepts:
    """Beam offsets at the near and far irises."""

    iris1: IrisOffset
    iris2: IrisOffset


@dataclass(frozen=True)
class BeamWalkingAxisModel:
    """One independent transverse-axis model for beam walking."""

    initial_offset_mm: float
    initial_angle_mrad: float
    m1_angle_coupling_mrad_per_mm: float = -5.0


@dataclass(frozen=True)
class BeamWalkingAxisState:
    """Mirror corrections for one transverse axis."""

    m1_offset_mm: float
    m2_angle_mrad: float


@dataclass(frozen=True)
class BeamWalkingModel:
    """Two-axis beam-walking model for two irises downstream of M2."""

    iris1_distance_mm: float
    iris2_distance_mm: float
    iris_radius_mm: float
    horizontal: BeamWalkingAxisModel
    vertical: BeamWalkingAxisModel


@dataclass(frozen=True)
class BeamWalkingState:
    """Named two-mirror alignment state for one storyboard frame."""

    name: str
    frame: int
    horizontal: BeamWalkingAxisState
    vertical: BeamWalkingAxisState


@dataclass(frozen=True)
class Ray3D:
    """Finite-radius geometric ray in millimeter scene coordinates."""

    origin_xyz_mm: VectorTuple
    direction_xyz: VectorTuple
    beam_radius_mm: float
    wavelength_nm: float = 561.0
    power_fraction: float = 1.0


@dataclass(frozen=True)
class PlaneMirror:
    """Finite circular plane mirror for import-safe ray tracing."""

    name: str
    center_xyz_mm: VectorTuple
    normal_xyz: VectorTuple
    clear_radius_mm: float
    reflectivity: float = 1.0


@dataclass(frozen=True)
class MirrorAdjustment:
    """Physical pitch/yaw adjustment applied to a steering mirror."""

    yaw_mrad: float = 0.0
    pitch_mrad: float = 0.0


@dataclass(frozen=True)
class CircularAperture:
    """Finite circular aperture in an opaque body plane."""

    name: str
    center_xyz_mm: VectorTuple
    normal_xyz: VectorTuple
    aperture_radius_mm: float
    body_radius_mm: float


@dataclass(frozen=True)
class RayInteraction:
    """One ray interaction with a finite optical element."""

    element_name: str
    element_kind: str
    status: str
    point_xyz_mm: VectorTuple
    local_y_mm: float
    local_z_mm: float
    radial_offset_mm: float
    clearance_margin_mm: float


@dataclass(frozen=True)
class BeamSegment:
    """One physical beam segment between two trace points."""

    start_xyz_mm: VectorTuple
    end_xyz_mm: VectorTuple
    power_fraction: float


@dataclass(frozen=True)
class RayTraceResult:
    """Ordered result of tracing a beam through optical elements."""

    interactions: tuple[RayInteraction, ...]
    segments: tuple[BeamSegment, ...]
    blocked_at: str


@dataclass(frozen=True)
class MirrorAlignmentSolution:
    """Numerical solution for steering two mirrors to target iris offsets."""

    m1_adjustment: MirrorAdjustment
    m2_adjustment: MirrorAdjustment
    residual_mm: float
    iterations: int
    converged: bool


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


def _add(a: VectorTuple, b: VectorTuple) -> VectorTuple:
    """Return the sum of two 3D vectors.

    Parameters
    ----------
    a
        First vector.
    b
        Second vector.

    Returns
    -------
    tuple[float, float, float]
        Vector sum.
    """

    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def _sub(a: VectorTuple, b: VectorTuple) -> VectorTuple:
    """Return the difference between two 3D vectors.

    Parameters
    ----------
    a
        Left-hand vector.
    b
        Right-hand vector.

    Returns
    -------
    tuple[float, float, float]
        Vector difference.
    """

    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


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


def _cross(a: VectorTuple, b: VectorTuple) -> VectorTuple:
    """Return the cross product of two 3D vectors.

    Parameters
    ----------
    a
        First vector.
    b
        Second vector.

    Returns
    -------
    tuple[float, float, float]
        Cross product.
    """

    return (
        (a[1] * b[2]) - (a[2] * b[1]),
        (a[2] * b[0]) - (a[0] * b[2]),
        (a[0] * b[1]) - (a[1] * b[0]),
    )


def _normalize(vector: VectorTuple) -> VectorTuple:
    """Return a unit-length 3D vector.

    Parameters
    ----------
    vector
        Vector to normalize.

    Returns
    -------
    tuple[float, float, float]
        Unit vector.
    """

    length = math.sqrt(_dot(vector, vector))
    if not math.isfinite(length) or length <= 0.0:
        raise ValueError(f"vector length must be positive; got {length!r}")
    return (vector[0] / length, vector[1] / length, vector[2] / length)


def _rotate_about_axis(
    vector: VectorTuple, *, axis: VectorTuple, angle_rad: float
) -> VectorTuple:
    """Rotate a vector about an axis using Rodrigues' formula.

    Parameters
    ----------
    vector
        Vector to rotate.
    axis
        Rotation axis.
    angle_rad
        Rotation angle in radians.

    Returns
    -------
    tuple[float, float, float]
        Rotated vector.
    """

    unit_axis = _normalize(axis)
    cos_angle = math.cos(angle_rad)
    sin_angle = math.sin(angle_rad)
    term_a = _scale(vector, cos_angle)
    term_b = _scale(_cross(unit_axis, vector), sin_angle)
    term_c = _scale(unit_axis, _dot(unit_axis, vector) * (1.0 - cos_angle))
    return _add(_add(term_a, term_b), term_c)


def adjusted_plane_mirror(
    mirror: PlaneMirror, *, adjustment: MirrorAdjustment
) -> PlaneMirror:
    """Return a mirror with pitch/yaw applied to its surface normal.

    Parameters
    ----------
    mirror
        Base finite plane mirror.
    adjustment
        Pitch and yaw adjustment in milliradians.

    Returns
    -------
    PlaneMirror
        Mirror with adjusted normal and unchanged center/aperture.
    """

    adjusted_normal = _normalize(mirror.normal_xyz)
    if adjustment.yaw_mrad:
        adjusted_normal = _rotate_about_axis(
            adjusted_normal,
            axis=(0.0, 0.0, 1.0),
            angle_rad=adjustment.yaw_mrad / 1000.0,
        )
    if adjustment.pitch_mrad:
        adjusted_normal = _rotate_about_axis(
            adjusted_normal,
            axis=(0.0, 1.0, 0.0),
            angle_rad=adjustment.pitch_mrad / 1000.0,
        )
    return PlaneMirror(
        name=mirror.name,
        center_xyz_mm=mirror.center_xyz_mm,
        normal_xyz=_normalize(adjusted_normal),
        clear_radius_mm=mirror.clear_radius_mm,
        reflectivity=mirror.reflectivity,
    )


def _plane_axes(normal: VectorTuple) -> tuple[VectorTuple, VectorTuple]:
    """Return stable local Y/Z axes tangent to a plane.

    Parameters
    ----------
    normal
        Plane normal vector.

    Returns
    -------
    tuple[tuple[float, float, float], tuple[float, float, float]]
        Local Y and local Z unit vectors.
    """

    unit_normal = _normalize(normal)
    z_reference = (0.0, 0.0, 1.0)
    if abs(_dot(unit_normal, z_reference)) > 0.98:
        z_reference = (0.0, 1.0, 0.0)
    local_z = _normalize(
        _sub(z_reference, _scale(unit_normal, _dot(unit_normal, z_reference)))
    )
    local_y = _normalize(_cross(local_z, unit_normal))
    return local_y, local_z


def _ray_plane_hit(
    *,
    origin: VectorTuple,
    direction: VectorTuple,
    plane_point: VectorTuple,
    plane_normal: VectorTuple,
    epsilon: float = 1e-9,
) -> VectorTuple | None:
    """Return a ray-plane hit point when the plane is in front of the ray.

    Parameters
    ----------
    origin
        Ray origin.
    direction
        Ray direction.
    plane_point
        Point on the plane.
    plane_normal
        Plane normal.
    epsilon
        Minimum positive ray travel distance.

    Returns
    -------
    tuple[float, float, float] or None
        Hit point, or ``None`` when the ray is parallel or behind the origin.
    """

    unit_direction = _normalize(direction)
    unit_normal = _normalize(plane_normal)
    denominator = _dot(unit_direction, unit_normal)
    if abs(denominator) < epsilon:
        return None
    distance = _dot(_sub(plane_point, origin), unit_normal) / denominator
    if distance < -epsilon:
        return None
    if abs(distance) < epsilon:
        distance = 0.0
    return _add(origin, _scale(unit_direction, distance))


def _local_plane_offsets(
    *, point: VectorTuple, center: VectorTuple, normal: VectorTuple
) -> tuple[float, float, float]:
    """Return local plane offsets and radial distance.

    Parameters
    ----------
    point
        World-space point on the plane.
    center
        World-space plane center.
    normal
        Plane normal.

    Returns
    -------
    tuple[float, float, float]
        Local Y offset, local Z offset, and radial offset.
    """

    local_y_axis, local_z_axis = _plane_axes(normal)
    delta = _sub(point, center)
    local_y = _dot(delta, local_y_axis)
    local_z = _dot(delta, local_z_axis)
    return local_y, local_z, math.hypot(local_y, local_z)


def trace_plane_mirror(
    *, ray: Ray3D, mirror: PlaneMirror
) -> tuple[RayInteraction, Ray3D | None]:
    """Trace one ray to a finite plane mirror.

    Parameters
    ----------
    ray
        Incident ray.
    mirror
        Finite plane mirror.

    Returns
    -------
    tuple[RayInteraction, Ray3D or None]
        Mirror interaction and reflected ray when the full beam footprint fits.
    """

    hit = _ray_plane_hit(
        origin=ray.origin_xyz_mm,
        direction=ray.direction_xyz,
        plane_point=mirror.center_xyz_mm,
        plane_normal=mirror.normal_xyz,
    )
    if hit is None:
        hit = ray.origin_xyz_mm
        local_y = 0.0
        local_z = 0.0
        radial_offset = math.inf
        margin = -math.inf
        return (
            RayInteraction(
                element_name=mirror.name,
                element_kind="mirror",
                status="missed_plane",
                point_xyz_mm=hit,
                local_y_mm=local_y,
                local_z_mm=local_z,
                radial_offset_mm=radial_offset,
                clearance_margin_mm=margin,
            ),
            None,
        )

    local_y, local_z, radial_offset = _local_plane_offsets(
        point=hit,
        center=mirror.center_xyz_mm,
        normal=mirror.normal_xyz,
    )
    margin = mirror.clear_radius_mm - (radial_offset + ray.beam_radius_mm)
    if margin < 0.0:
        return (
            RayInteraction(
                element_name=mirror.name,
                element_kind="mirror",
                status="missed_clear_aperture",
                point_xyz_mm=hit,
                local_y_mm=local_y,
                local_z_mm=local_z,
                radial_offset_mm=radial_offset,
                clearance_margin_mm=margin,
            ),
            None,
        )

    unit_direction = _normalize(ray.direction_xyz)
    unit_normal = _normalize(mirror.normal_xyz)
    reflected_direction = _normalize(
        _sub(
            unit_direction, _scale(unit_normal, 2.0 * _dot(unit_direction, unit_normal))
        )
    )
    return (
        RayInteraction(
            element_name=mirror.name,
            element_kind="mirror",
            status="hit",
            point_xyz_mm=hit,
            local_y_mm=local_y,
            local_z_mm=local_z,
            radial_offset_mm=radial_offset,
            clearance_margin_mm=margin,
        ),
        Ray3D(
            origin_xyz_mm=hit,
            direction_xyz=reflected_direction,
            beam_radius_mm=ray.beam_radius_mm,
            wavelength_nm=ray.wavelength_nm,
            power_fraction=ray.power_fraction * mirror.reflectivity,
        ),
    )


def trace_circular_aperture(
    *, ray: Ray3D, aperture: CircularAperture
) -> tuple[RayInteraction, Ray3D | None]:
    """Trace one ray to a finite circular aperture.

    Parameters
    ----------
    ray
        Incident ray.
    aperture
        Circular aperture in an opaque body.

    Returns
    -------
    tuple[RayInteraction, Ray3D or None]
        Aperture interaction and transmitted ray when any beam power remains.
    """

    hit = _ray_plane_hit(
        origin=ray.origin_xyz_mm,
        direction=ray.direction_xyz,
        plane_point=aperture.center_xyz_mm,
        plane_normal=aperture.normal_xyz,
    )
    if hit is None:
        hit = ray.origin_xyz_mm
        return (
            RayInteraction(
                element_name=aperture.name,
                element_kind="aperture",
                status="missed_plane",
                point_xyz_mm=hit,
                local_y_mm=0.0,
                local_z_mm=0.0,
                radial_offset_mm=math.inf,
                clearance_margin_mm=-math.inf,
            ),
            None,
        )

    local_y, local_z, radial_offset = _local_plane_offsets(
        point=hit,
        center=aperture.center_xyz_mm,
        normal=aperture.normal_xyz,
    )
    margin = aperture.aperture_radius_mm - (radial_offset + ray.beam_radius_mm)
    if margin >= 0.0:
        status = "passed"
        transmitted_power = ray.power_fraction
    elif radial_offset - ray.beam_radius_mm <= aperture.aperture_radius_mm:
        status = "clipped"
        transmitted_power = ray.power_fraction * 0.5
    else:
        status = "blocked"
        transmitted_power = 0.0

    interaction = RayInteraction(
        element_name=aperture.name,
        element_kind="aperture",
        status=status,
        point_xyz_mm=hit,
        local_y_mm=local_y,
        local_z_mm=local_z,
        radial_offset_mm=radial_offset,
        clearance_margin_mm=margin,
    )
    if transmitted_power <= 0.0:
        return interaction, None
    return (
        interaction,
        Ray3D(
            origin_xyz_mm=hit,
            direction_xyz=_normalize(ray.direction_xyz),
            beam_radius_mm=ray.beam_radius_mm,
            wavelength_nm=ray.wavelength_nm,
            power_fraction=transmitted_power,
        ),
    )


def _segment_to_interaction(ray: Ray3D, interaction: RayInteraction) -> BeamSegment:
    """Return a beam segment from the ray origin to an interaction point.

    Parameters
    ----------
    ray
        Ray before the interaction.
    interaction
        Interaction reached by the ray.

    Returns
    -------
    BeamSegment
        Segment ending at the interaction point.
    """

    return BeamSegment(
        start_xyz_mm=ray.origin_xyz_mm,
        end_xyz_mm=interaction.point_xyz_mm,
        power_fraction=ray.power_fraction,
    )


def _segment_after_ray(ray: Ray3D, *, length_mm: float) -> BeamSegment:
    """Return a downstream segment that continues an unblocked ray.

    Parameters
    ----------
    ray
        Ray after the last interaction.
    length_mm
        Segment length to display.

    Returns
    -------
    BeamSegment
        Segment continuing downstream from the ray origin.
    """

    unit_direction = _normalize(ray.direction_xyz)
    return BeamSegment(
        start_xyz_mm=ray.origin_xyz_mm,
        end_xyz_mm=_add(ray.origin_xyz_mm, _scale(unit_direction, length_mm)),
        power_fraction=ray.power_fraction,
    )


def trace_two_mirror_two_iris_system(
    *,
    source_ray: Ray3D,
    m1: PlaneMirror,
    m2: PlaneMirror,
    iris1: CircularAperture,
    iris2: CircularAperture,
    downstream_length_mm: float = 25.0,
) -> RayTraceResult:
    """Trace a beam through two mirrors followed by two irises.

    Parameters
    ----------
    source_ray
        Incoming ray before the first mirror.
    m1
        First steering mirror.
    m2
        Second steering mirror.
    iris1
        Near alignment iris.
    iris2
        Far alignment iris.
    downstream_length_mm
        Length of the displayed downstream segment after Iris 2 when the beam
        is not blocked.

    Returns
    -------
    RayTraceResult
        Ordered interactions, physical segments, and blocking element name.
    """

    interactions: list[RayInteraction] = []
    segments: list[BeamSegment] = []
    current_ray = source_ray

    for mirror in (m1, m2):
        interaction, reflected_ray = trace_plane_mirror(
            ray=current_ray,
            mirror=mirror,
        )
        interactions.append(interaction)
        segments.append(_segment_to_interaction(current_ray, interaction))
        if reflected_ray is None:
            return RayTraceResult(
                interactions=tuple(interactions),
                segments=tuple(segments),
                blocked_at=interaction.element_name,
            )
        current_ray = reflected_ray

    for aperture in (iris1, iris2):
        interaction, transmitted_ray = trace_circular_aperture(
            ray=current_ray,
            aperture=aperture,
        )
        interactions.append(interaction)
        segments.append(_segment_to_interaction(current_ray, interaction))
        if transmitted_ray is None:
            return RayTraceResult(
                interactions=tuple(interactions),
                segments=tuple(segments),
                blocked_at=interaction.element_name,
            )
        current_ray = transmitted_ray

    segments.append(_segment_after_ray(current_ray, length_mm=downstream_length_mm))
    return RayTraceResult(
        interactions=tuple(interactions),
        segments=tuple(segments),
        blocked_at="",
    )


def trace_two_mirror_iris_intercepts(
    *,
    source_ray: Ray3D,
    m1: PlaneMirror,
    m2: PlaneMirror,
    iris1: CircularAperture,
    iris2: CircularAperture,
) -> BeamIntercepts:
    """Return downstream iris offsets after two finite mirror reflections.

    The mirror clear apertures are enforced. The iris apertures are treated as
    measurement planes so this helper can solve and report off-aperture target
    positions without prematurely clipping the beam.

    Parameters
    ----------
    source_ray
        Incoming ray before the first mirror.
    m1
        First steering mirror.
    m2
        Second steering mirror.
    iris1
        Near iris measurement plane.
    iris2
        Far iris measurement plane.

    Returns
    -------
    BeamIntercepts
        World-Y and world-Z offsets at the two iris planes.

    Raises
    ------
    ValueError
        If either mirror is missed or either iris plane is unreachable.
    """

    m1_interaction, after_m1 = trace_plane_mirror(ray=source_ray, mirror=m1)
    if after_m1 is None:
        raise ValueError(
            f"source ray did not reflect from {m1.name}: {m1_interaction.status}"
        )
    m2_interaction, after_m2 = trace_plane_mirror(ray=after_m1, mirror=m2)
    if after_m2 is None:
        raise ValueError(
            f"beam did not reflect from {m2.name}: {m2_interaction.status}"
        )

    iris1_hit = _ray_plane_hit(
        origin=after_m2.origin_xyz_mm,
        direction=after_m2.direction_xyz,
        plane_point=iris1.center_xyz_mm,
        plane_normal=iris1.normal_xyz,
    )
    iris2_hit = _ray_plane_hit(
        origin=after_m2.origin_xyz_mm,
        direction=after_m2.direction_xyz,
        plane_point=iris2.center_xyz_mm,
        plane_normal=iris2.normal_xyz,
    )
    if iris1_hit is None or iris2_hit is None:
        raise ValueError("reflected beam does not reach both iris planes")

    return BeamIntercepts(
        iris1=IrisOffset(
            y_mm=iris1_hit[1] - iris1.center_xyz_mm[1],
            z_mm=iris1_hit[2] - iris1.center_xyz_mm[2],
        ),
        iris2=IrisOffset(
            y_mm=iris2_hit[1] - iris2.center_xyz_mm[1],
            z_mm=iris2_hit[2] - iris2.center_xyz_mm[2],
        ),
    )


def _intercepts_vector(intercepts: BeamIntercepts) -> tuple[float, float, float, float]:
    """Return a four-component vector from two iris intercepts.

    Parameters
    ----------
    intercepts
        Two-iris intercept record.

    Returns
    -------
    tuple[float, float, float, float]
        Iris 1 Y/Z followed by Iris 2 Y/Z.
    """

    return (
        intercepts.iris1.y_mm,
        intercepts.iris1.z_mm,
        intercepts.iris2.y_mm,
        intercepts.iris2.z_mm,
    )


def _vector_norm(values: Sequence[float]) -> float:
    """Return the Euclidean norm of a numeric vector.

    Parameters
    ----------
    values
        Numeric vector components.

    Returns
    -------
    float
        Euclidean norm.
    """

    return math.sqrt(sum(value * value for value in values))


def _solve_linear_system(
    matrix: Sequence[Sequence[float]], vector: Sequence[float]
) -> tuple[float, ...]:
    """Solve a small dense linear system with partial pivoting.

    Parameters
    ----------
    matrix
        Square coefficient matrix.
    vector
        Right-hand side vector.

    Returns
    -------
    tuple[float, ...]
        Solution vector.

    Raises
    ------
    ValueError
        If the system is singular or dimensions are inconsistent.
    """

    size = len(vector)
    if size == 0 or len(matrix) != size or any(len(row) != size for row in matrix):
        raise ValueError("linear system dimensions are inconsistent")

    augmented = [list(matrix[row]) + [float(vector[row])] for row in range(size)]
    for column in range(size):
        pivot = max(range(column, size), key=lambda row: abs(augmented[row][column]))
        if abs(augmented[pivot][column]) < 1e-12:
            raise ValueError("linear system is singular")
        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]

        pivot_value = augmented[column][column]
        for index in range(column, size + 1):
            augmented[column][index] /= pivot_value

        for row in range(size):
            if row == column:
                continue
            factor = augmented[row][column]
            for index in range(column, size + 1):
                augmented[row][index] -= factor * augmented[column][index]

    return tuple(augmented[row][size] for row in range(size))


def solve_two_mirror_alignment(
    *,
    source_ray: Ray3D,
    m1: PlaneMirror,
    m2: PlaneMirror,
    iris1: CircularAperture,
    iris2: CircularAperture,
    target_offsets: BeamIntercepts,
    initial_m1_adjustment: MirrorAdjustment | None = None,
    initial_m2_adjustment: MirrorAdjustment | None = None,
    tolerance_mm: float = 1e-3,
    max_iterations: int = 25,
    finite_difference_step_mrad: float = 0.1,
    max_step_mrad: float = 100.0,
) -> MirrorAlignmentSolution:
    """Solve mirror pitch/yaw settings for requested iris offsets.

    Parameters
    ----------
    source_ray
        Incoming ray before the first mirror.
    m1
        First finite steering mirror.
    m2
        Second finite steering mirror.
    iris1
        Near iris measurement plane.
    iris2
        Far iris measurement plane.
    target_offsets
        Requested world-Y/Z offsets at the two iris planes.
    initial_m1_adjustment
        Optional starting pitch/yaw adjustment for M1.
    initial_m2_adjustment
        Optional starting pitch/yaw adjustment for M2.
    tolerance_mm
        Residual norm below which the solution is considered converged.
    max_iterations
        Maximum damped Newton iterations.
    finite_difference_step_mrad
        Perturbation used to estimate the numerical Jacobian.
    max_step_mrad
        Maximum absolute Newton step per variable before damping.

    Returns
    -------
    MirrorAlignmentSolution
        Best mirror adjustments found by the numerical solve.

    Raises
    ------
    ValueError
        If the initial mirror geometry cannot produce iris-plane intercepts.
    """

    if tolerance_mm <= 0.0:
        raise ValueError("tolerance_mm must be positive")
    if finite_difference_step_mrad <= 0.0:
        raise ValueError("finite_difference_step_mrad must be positive")
    if max_step_mrad <= 0.0:
        raise ValueError("max_step_mrad must be positive")
    target = _intercepts_vector(target_offsets)
    start_m1 = initial_m1_adjustment or MirrorAdjustment()
    start_m2 = initial_m2_adjustment or MirrorAdjustment()
    values = [
        start_m1.yaw_mrad,
        start_m1.pitch_mrad,
        start_m2.yaw_mrad,
        start_m2.pitch_mrad,
    ]

    def evaluate(candidate: Sequence[float]) -> tuple[float, ...] | None:
        """Return iris-intercept residuals for one mirror-adjustment vector.

        Parameters
        ----------
        candidate
            Sequence containing M1 yaw, M1 pitch, M2 yaw, and M2 pitch in
            milliradians.

        Returns
        -------
        tuple[float, ...] or None
            Difference between actual and target iris intercepts, or ``None``
            when the candidate mirror adjustments do not reach both iris
            planes.
        """

        adjusted_m1 = adjusted_plane_mirror(
            m1,
            adjustment=MirrorAdjustment(
                yaw_mrad=candidate[0],
                pitch_mrad=candidate[1],
            ),
        )
        adjusted_m2 = adjusted_plane_mirror(
            m2,
            adjustment=MirrorAdjustment(
                yaw_mrad=candidate[2],
                pitch_mrad=candidate[3],
            ),
        )
        try:
            intercepts = trace_two_mirror_iris_intercepts(
                source_ray=source_ray,
                m1=adjusted_m1,
                m2=adjusted_m2,
                iris1=iris1,
                iris2=iris2,
            )
        except ValueError:
            return None
        actual = _intercepts_vector(intercepts)
        return tuple(actual[index] - target[index] for index in range(4))

    residual = evaluate(values)
    if residual is None:
        raise ValueError("initial mirror adjustments do not reach both iris planes")
    best_values = list(values)
    best_residual = residual
    best_norm = _vector_norm(best_residual)
    iterations = 0

    for iterations in range(1, max_iterations + 1):
        if best_norm <= tolerance_mm:
            break

        columns: list[tuple[float, ...]] = []
        for column in range(4):
            perturbed = list(best_values)
            perturbed[column] += finite_difference_step_mrad
            perturbed_residual = evaluate(perturbed)
            if perturbed_residual is None:
                perturbed = list(best_values)
                perturbed[column] -= finite_difference_step_mrad
                perturbed_residual = evaluate(perturbed)
                scale = -finite_difference_step_mrad
            else:
                scale = finite_difference_step_mrad
            if perturbed_residual is None:
                raise ValueError("unable to estimate alignment Jacobian")
            columns.append(
                tuple(
                    (perturbed_residual[row] - best_residual[row]) / scale
                    for row in range(4)
                )
            )

        jacobian = [[columns[column][row] for column in range(4)] for row in range(4)]
        try:
            delta = _solve_linear_system(
                jacobian,
                tuple(-component for component in best_residual),
            )
        except ValueError:
            break

        largest_step = max(abs(component) for component in delta)
        if largest_step > max_step_mrad:
            delta = tuple(
                component * max_step_mrad / largest_step for component in delta
            )

        accepted = False
        damping = 1.0
        for _attempt in range(12):
            candidate = [
                best_values[index] + (damping * delta[index]) for index in range(4)
            ]
            candidate_residual = evaluate(candidate)
            if candidate_residual is not None:
                candidate_norm = _vector_norm(candidate_residual)
                if candidate_norm < best_norm:
                    best_values = candidate
                    best_residual = candidate_residual
                    best_norm = candidate_norm
                    accepted = True
                    break
            damping *= 0.5

        if not accepted:
            break

    return MirrorAlignmentSolution(
        m1_adjustment=MirrorAdjustment(
            yaw_mrad=best_values[0],
            pitch_mrad=best_values[1],
        ),
        m2_adjustment=MirrorAdjustment(
            yaw_mrad=best_values[2],
            pitch_mrad=best_values[3],
        ),
        residual_mm=best_norm,
        iterations=iterations,
        converged=best_norm <= tolerance_mm,
    )


DEFAULT_WALKING_BEAM_MODEL = BeamWalkingModel(
    iris1_distance_mm=76.2,
    iris2_distance_mm=127.0,
    iris_radius_mm=1.25,
    horizontal=BeamWalkingAxisModel(
        initial_offset_mm=4.8,
        initial_angle_mrad=-90.0,
    ),
    vertical=BeamWalkingAxisModel(
        initial_offset_mm=-4.0,
        initial_angle_mrad=55.0,
    ),
)


def _axis_intercept(
    model: BeamWalkingAxisModel, state: BeamWalkingAxisState, *, distance_mm: float
) -> float:
    """Return one-axis beam offset at a downstream distance.

    Parameters
    ----------
    model
        One-axis initial beam error.
    state
        One-axis mirror corrections.
    distance_mm
        Distance downstream of the second mirror.

    Returns
    -------
    float
        Transverse beam offset at the requested distance.
    """

    angle = (
        model.initial_angle_mrad
        + state.m2_angle_mrad
        + (model.m1_angle_coupling_mrad_per_mm * state.m1_offset_mm)
    ) / 1000.0
    return model.initial_offset_mm + state.m1_offset_mm + (angle * distance_mm)


def compute_axis_intercepts(
    *,
    axis_model: BeamWalkingAxisModel,
    axis_state: BeamWalkingAxisState,
    iris1_distance_mm: float,
    iris2_distance_mm: float,
) -> tuple[float, float]:
    """Return one-axis offsets at Iris 1 and Iris 2.

    Parameters
    ----------
    axis_model
        Initial one-axis beam error.
    axis_state
        One-axis mirror corrections.
    iris1_distance_mm
        Distance from M2 to Iris 1.
    iris2_distance_mm
        Distance from M2 to Iris 2.

    Returns
    -------
    tuple[float, float]
        Offsets at Iris 1 and Iris 2.
    """

    return (
        _axis_intercept(
            axis_model,
            axis_state,
            distance_mm=iris1_distance_mm,
        ),
        _axis_intercept(
            axis_model,
            axis_state,
            distance_mm=iris2_distance_mm,
        ),
    )


def compute_beam_intercepts(
    model: BeamWalkingModel, state: BeamWalkingState
) -> BeamIntercepts:
    """Return horizontal and vertical beam offsets at both irises.

    Parameters
    ----------
    model
        Two-axis beam-walking model.
    state
        Alignment state to evaluate.

    Returns
    -------
    BeamIntercepts
        Offset at Iris 1 and Iris 2.
    """

    iris1_y, iris2_y = compute_axis_intercepts(
        axis_model=model.horizontal,
        axis_state=state.horizontal,
        iris1_distance_mm=model.iris1_distance_mm,
        iris2_distance_mm=model.iris2_distance_mm,
    )
    iris1_z, iris2_z = compute_axis_intercepts(
        axis_model=model.vertical,
        axis_state=state.vertical,
        iris1_distance_mm=model.iris1_distance_mm,
        iris2_distance_mm=model.iris2_distance_mm,
    )
    return BeamIntercepts(
        iris1=IrisOffset(y_mm=iris1_y, z_mm=iris1_z),
        iris2=IrisOffset(y_mm=iris2_y, z_mm=iris2_z),
    )


def alignment_error_magnitude(intercepts: BeamIntercepts) -> float:
    """Return root-sum-square error across both iris readouts.

    Parameters
    ----------
    intercepts
        Beam offsets at both irises.

    Returns
    -------
    float
        Combined alignment error in millimeters.
    """

    return math.sqrt(
        (intercepts.iris1.y_mm * intercepts.iris1.y_mm)
        + (intercepts.iris1.z_mm * intercepts.iris1.z_mm)
        + (intercepts.iris2.y_mm * intercepts.iris2.y_mm)
        + (intercepts.iris2.z_mm * intercepts.iris2.z_mm)
    )


def beam_passes_irises(model: BeamWalkingModel, intercepts: BeamIntercepts) -> bool:
    """Return whether the beam is within both iris apertures.

    Parameters
    ----------
    model
        Beam-walking model with the open iris radius.
    intercepts
        Beam offsets at both irises.

    Returns
    -------
    bool
        ``True`` when both radial offsets are within the iris radius.
    """

    return all(
        math.hypot(offset.y_mm, offset.z_mm) <= model.iris_radius_mm
        for offset in (intercepts.iris1, intercepts.iris2)
    )


def _center_iris1_axis(
    model: BeamWalkingModel,
    axis_model: BeamWalkingAxisModel,
    axis_state: BeamWalkingAxisState,
) -> BeamWalkingAxisState:
    """Return an M1 correction that centers Iris 1 for one axis.

    Parameters
    ----------
    model
        Beam-walking geometry.
    axis_model
        One-axis initial beam error.
    axis_state
        Existing one-axis correction state.

    Returns
    -------
    BeamWalkingAxisState
        Updated one-axis correction state.
    """

    uncoupled_angle = axis_model.initial_angle_mrad + axis_state.m2_angle_mrad
    denominator = 1.0 + (
        axis_model.m1_angle_coupling_mrad_per_mm * model.iris1_distance_mm / 1000.0
    )
    return BeamWalkingAxisState(
        m1_offset_mm=-(
            axis_model.initial_offset_mm
            + ((uncoupled_angle / 1000.0) * model.iris1_distance_mm)
        )
        / denominator,
        m2_angle_mrad=axis_state.m2_angle_mrad,
    )


def _center_iris2_axis(
    model: BeamWalkingModel,
    axis_model: BeamWalkingAxisModel,
    axis_state: BeamWalkingAxisState,
) -> BeamWalkingAxisState:
    """Return an M2 correction that centers Iris 2 for one axis.

    Parameters
    ----------
    model
        Beam-walking geometry.
    axis_model
        One-axis initial beam error.
    axis_state
        Existing one-axis correction state.

    Returns
    -------
    BeamWalkingAxisState
        Updated one-axis correction state.
    """

    angle_mrad = (
        (
            -(
                (axis_model.initial_offset_mm + axis_state.m1_offset_mm)
                / model.iris2_distance_mm
            )
            * 1000.0
        )
        - axis_model.initial_angle_mrad
        - (axis_model.m1_angle_coupling_mrad_per_mm * axis_state.m1_offset_mm)
    )
    return BeamWalkingAxisState(
        m1_offset_mm=axis_state.m1_offset_mm,
        m2_angle_mrad=angle_mrad,
    )


def _center_iris1(
    model: BeamWalkingModel, state: BeamWalkingState, *, name: str, frame: int
) -> BeamWalkingState:
    """Return a two-axis state after applying the M1 centering step.

    Parameters
    ----------
    model
        Beam-walking geometry.
    state
        Current two-axis alignment state.
    name
        Name for the returned storyboard state.
    frame
        Timeline frame for the returned storyboard state.

    Returns
    -------
    BeamWalkingState
        Updated two-axis alignment state.
    """

    return BeamWalkingState(
        name=name,
        frame=frame,
        horizontal=_center_iris1_axis(model, model.horizontal, state.horizontal),
        vertical=_center_iris1_axis(model, model.vertical, state.vertical),
    )


def _center_iris2(
    model: BeamWalkingModel, state: BeamWalkingState, *, name: str, frame: int
) -> BeamWalkingState:
    """Return a two-axis state after applying the M2 centering step.

    Parameters
    ----------
    model
        Beam-walking geometry.
    state
        Current two-axis alignment state.
    name
        Name for the returned storyboard state.
    frame
        Timeline frame for the returned storyboard state.

    Returns
    -------
    BeamWalkingState
        Updated two-axis alignment state.
    """

    return BeamWalkingState(
        name=name,
        frame=frame,
        horizontal=_center_iris2_axis(model, model.horizontal, state.horizontal),
        vertical=_center_iris2_axis(model, model.vertical, state.vertical),
    )


def exact_alignment_state(
    model: BeamWalkingModel, *, name: str, frame: int
) -> BeamWalkingState:
    """Return the analytic two-axis state that centers both irises.

    Parameters
    ----------
    model
        Beam-walking geometry.
    name
        Name for the returned storyboard state.
    frame
        Timeline frame for the returned storyboard state.

    Returns
    -------
    BeamWalkingState
        State with zero beam offset at both irises.
    """

    return BeamWalkingState(
        name=name,
        frame=frame,
        horizontal=BeamWalkingAxisState(
            m1_offset_mm=-model.horizontal.initial_offset_mm,
            m2_angle_mrad=-model.horizontal.initial_angle_mrad
            + (
                model.horizontal.m1_angle_coupling_mrad_per_mm
                * model.horizontal.initial_offset_mm
            ),
        ),
        vertical=BeamWalkingAxisState(
            m1_offset_mm=-model.vertical.initial_offset_mm,
            m2_angle_mrad=-model.vertical.initial_angle_mrad
            + (
                model.vertical.m1_angle_coupling_mrad_per_mm
                * model.vertical.initial_offset_mm
            ),
        ),
    )


def iterative_alignment_sequence(
    model: BeamWalkingModel = DEFAULT_WALKING_BEAM_MODEL,
    *,
    frames: Sequence[int] = (1, 36, 72, 108, 144, 168),
) -> tuple[BeamWalkingState, ...]:
    """Return the deterministic two-mirror walking-beam storyboard.

    Parameters
    ----------
    model
        Beam-walking geometry to use for the sequence.
    frames
        Six timeline frames for gross error, M1, M2, M1 refinement, M2
        refinement, and final aligned hold.

    Returns
    -------
    tuple[BeamWalkingState, ...]
        Ordered alignment states.
    """

    if len(frames) != 6:
        raise ValueError("frames must contain exactly six entries")

    gross = BeamWalkingState(
        name="gross_misalignment",
        frame=int(frames[0]),
        horizontal=BeamWalkingAxisState(m1_offset_mm=0.0, m2_angle_mrad=0.0),
        vertical=BeamWalkingAxisState(m1_offset_mm=0.0, m2_angle_mrad=0.0),
    )
    m1_centered = _center_iris1(
        model,
        gross,
        name="m1_centers_iris1",
        frame=int(frames[1]),
    )
    m2_centered = _center_iris2(
        model,
        m1_centered,
        name="m2_centers_iris2",
        frame=int(frames[2]),
    )
    m1_refined = _center_iris1(
        model,
        m2_centered,
        name="m1_refinement",
        frame=int(frames[3]),
    )
    m2_refined = _center_iris2(
        model,
        m1_refined,
        name="m2_refinement",
        frame=int(frames[4]),
    )
    aligned = exact_alignment_state(model, name="aligned_hold", frame=int(frames[5]))
    return (gross, m1_centered, m2_centered, m1_refined, m2_refined, aligned)
