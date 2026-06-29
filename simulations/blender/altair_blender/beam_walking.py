"""Import-safe model for walking a laser beam through two irises."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
import math


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
