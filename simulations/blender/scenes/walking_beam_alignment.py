"""Generate the two-mirror walking-beam alignment teaching scene."""

from __future__ import annotations

from collections.abc import Mapping
import math
import os
from pathlib import Path
import sys
from typing import Any
from typing import NamedTuple


def _ensure_repo_root_on_path() -> None:
    """Ensure direct script execution can import the repository package."""

    repo_root = Path(__file__).resolve().parents[3]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))


_ensure_repo_root_on_path()

from simulations.blender.altair_blender.beam_walking import (  # noqa: E402
    BeamIntercepts,
    BeamWalkingAxisModel,
    BeamWalkingModel,
    BeamWalkingState,
    CircularAperture,
    IrisOffset,
    MirrorAdjustment,
    PlaneMirror,
    Ray3D,
    RayTraceResult,
    adjusted_plane_mirror,
    exact_alignment_state,
    iterative_alignment_sequence,
    trace_two_mirror_two_iris_system,
)
from simulations.blender.altair_blender.prescriptions import (  # noqa: E402
    ID25_IRIS,
    KM100CP_MOUNT,
    PH2_POST_HOLDER,
    TR15_POST,
)
from simulations.blender.altair_blender.scene import RENDER_PRESETS  # noqa: E402

SCENE_NAME = "walking_beam_alignment"


class BeamPathPoint(NamedTuple):
    """Named world-space point on the displayed beam path."""

    name: str
    xyz: tuple[float, float, float]


class DownstreamBeamPath(NamedTuple):
    """Named points for the animated beam after the second mirror."""

    start_xyz: tuple[float, float, float]
    iris1_xyz: tuple[float, float, float]
    iris2_xyz: tuple[float, float, float]
    exit_xyz: tuple[float, float, float]
    visible_end_xyz: tuple[float, float, float]
    blocked_at: str
    beam_visible: bool
    iris1_visible: bool
    iris2_visible: bool


class BeamSegmentPath(NamedTuple):
    """World-space start and end points for one displayed beam segment."""

    start_xyz: tuple[float, float, float]
    end_xyz: tuple[float, float, float]


class CameraPose(NamedTuple):
    """Import-safe camera pose used by scene contract tests."""

    location_xyz: tuple[float, float, float]
    target_xyz: tuple[float, float, float]
    lens_mm: float


class WideCameraPlan(NamedTuple):
    """Import-safe wide camera motion plan used by scene contract tests."""

    target_xyz: tuple[float, float, float]
    distance_mm: float
    elevation_mm: float
    end_target_xyz: tuple[float, float, float]
    end_distance_mm: float
    end_elevation_mm: float


class StoryboardCaption(NamedTuple):
    """Caption text for one alignment storyboard state."""

    state_name: str
    frame: int
    text: str


class LabelStyle(NamedTuple):
    """Scene-local label material styling."""

    color: tuple[float, float, float, float]
    emission_strength: float


DEFAULT_PARAMETERS: dict[str, Any] = {
    "wavelength_nm": 561.0,
    "beam_diameter_mm": 1.0,
    "beam_visual_diameter_mm": 1.35,
    "alignment_aperture_diameter_mm": 2.5,
    "iris_display_aperture_mm": 2.5,
    "iris_spot_radius_mm": 1.25,
    "iris_reticle_radius_mm": 4.0,
    "iris_reticle_faces": "both",
    "hole_grid_spacing_mm": 25.4,
    "hole_grid_layout": {
        "m1": (-2, -2),
        "m2": (-2, 0),
        "iris_1": (1, 0),
        "iris_2": (6, 0),
    },
    "table_center_x_mm": 0.0,
    "table_center_y_mm": 0.0,
    "table_center_z_mm": -8.0,
    "table_length_mm": 330.0,
    "table_width_mm": 115.0,
    "table_top_z_mm": -5.0,
    "optical_axis_z_mm": 45.8,
    "initial_horizontal_offset_mm": 4.8,
    "initial_horizontal_angle_mrad": -90.0,
    "initial_vertical_offset_mm": -4.0,
    "initial_vertical_angle_mrad": 55.0,
    "beam_path_offset_exaggeration": 2.0,
    "spot_display_exaggeration": 2.0,
    "mirror_display_exaggeration": 0.18,
    "iris_source": ID25_IRIS.source_notes,
    "post_holder_source": PH2_POST_HOLDER.source_notes,
    "post_source": TR15_POST.source_notes,
    "mirror_mount_source": KM100CP_MOUNT.source_notes,
    "show_minimal_labels": True,
    "label_color": (1.0, 0.96, 0.7, 1.0),
    "label_emission_strength": 1.55,
    "show_storyboard_captions": True,
    "storyboard_caption_location_mm": (76.2, -45.0, 86.0),
    "storyboard_caption_size_mm": 3.4,
    "storyboard_captions": {
        "gross_misalignment": "Start: beam misses both irises",
        "m1_centers_iris1": "M1 adjust: center Iris 1",
        "m2_centers_iris2": "M2 adjust: center Iris 2",
        "m1_refinement": "M1 refine: recenter Iris 1",
        "m2_refinement": "M2 refine: recenter Iris 2",
        "aligned_hold": "Aligned: both irises centered",
    },
    "wide_camera_name": "Wide Setup Camera",
    "iris_closeup_camera_name": "Iris Close-Up Camera",
    "hero_camera_name": "Hero Camera",
    "iris_closeup_lens_mm": 32.0,
    "iris_closeup_distance_y_mm": 215.0,
    "iris_closeup_elevation_mm": 38.0,
    "softbox_power": 900.0,
    "softbox_size_mm": 86.0,
    "fill_power": 330.0,
    "rim_light_power": 420.0,
    "wide_camera_distance_mm": 345.0,
    "wide_camera_elevation_mm": 136.0,
    "wide_camera_end_distance_mm": 330.0,
    "wide_camera_end_elevation_mm": 122.0,
    "default_render_preset": "final",
    "render_presets": RENDER_PRESETS,
    "final_video_output_stem": "walking_beam_alignment",
    "scene_labels": (
        "M1",
        "M2",
        "Iris 1",
        "Iris 2",
        "same beam height",
    ),
    "mirror_surface_offset_mm": 7.0,
    "m1_yaw_deg": -45.0,
    "m2_yaw_deg": 135.0,
    "frame_start": 1,
    "frame_m1_centers_iris1": 36,
    "frame_m2_centers_iris2": 72,
    "frame_m1_refinement": 108,
    "frame_m2_refinement": 144,
    "frame_end": 168,
}


def _parse_output_path(argv: list[str]) -> str | None:
    """Parse the optional Blender output path from script arguments.

    Parameters
    ----------
    argv
        Process argument vector supplied by Blender or Python.

    Returns
    -------
    str or None
        Output path after Blender's ``--`` separator, when provided.
    """

    if "--" not in argv:
        return None
    separator = argv.index("--")
    extra = argv[separator + 1 :]
    if not extra:
        return None
    return extra[0]


def _grid_position_mm(
    params: Mapping[str, Any], component_name: str
) -> tuple[float, float]:
    """Return the table-grid position for a named component.

    Parameters
    ----------
    params
        Scene parameter mapping.
    component_name
        Name from the ``hole_grid_layout`` mapping.

    Returns
    -------
    tuple[float, float]
        X/Y position in millimeters.
    """

    grid_x, grid_y = params["hole_grid_layout"][component_name]
    spacing = float(params["hole_grid_spacing_mm"])
    return (float(grid_x) * spacing, float(grid_y) * spacing)


def _component_centers(
    params: Mapping[str, Any],
) -> dict[str, tuple[float, float, float]]:
    """Return the optical-axis center for each component.

    Parameters
    ----------
    params
        Scene parameter mapping.

    Returns
    -------
    dict[str, tuple[float, float, float]]
        Component center coordinates.
    """

    axis_z = float(params["optical_axis_z_mm"])
    return {
        name: (*_grid_position_mm(params, name), axis_z)
        for name in ("m1", "m2", "iris_1", "iris_2")
    }


def _mirror_reflective_normal(yaw_deg: float) -> tuple[float, float, float]:
    """Return the world-space normal of the visible mirror face.

    Parameters
    ----------
    yaw_deg
        Mirror mount yaw in degrees.

    Returns
    -------
    tuple[float, float, float]
        Unit normal of the local negative-X mirror face.
    """

    yaw_rad = math.radians(yaw_deg)
    return (-math.cos(yaw_rad), -math.sin(yaw_rad), 0.0)


def _reflect_direction(
    direction: tuple[float, float, float],
    normal: tuple[float, float, float],
) -> tuple[float, float, float]:
    """Reflect a direction vector about a mirror normal.

    Parameters
    ----------
    direction
        Incident direction vector.
    normal
        Mirror normal vector.

    Returns
    -------
    tuple[float, float, float]
        Unit reflected direction vector.
    """

    dot_product = sum(direction[index] * normal[index] for index in range(3))
    reflected = tuple(
        direction[index] - (2.0 * dot_product * normal[index]) for index in range(3)
    )
    length = math.sqrt(sum(component * component for component in reflected))
    if length <= 0.0:
        raise ValueError("Reflected direction must have positive length.")
    return tuple(component / length for component in reflected)


def _mirror_plane_point(
    center: tuple[float, float, float], *, yaw_deg: float, offset_mm: float
) -> tuple[float, float, float]:
    """Return one point on the visible mirror face plane.

    Parameters
    ----------
    center
        Optical center of the mirror mount.
    yaw_deg
        Mirror mount yaw in degrees.
    offset_mm
        Offset from mount center to the visible mirror face along local
        negative X.

    Returns
    -------
    tuple[float, float, float]
        World-space point on the mirror face plane.
    """

    yaw_rad = math.radians(yaw_deg)
    return (
        center[0] - (offset_mm * math.cos(yaw_rad)),
        center[1] - (offset_mm * math.sin(yaw_rad)),
        center[2],
    )


def _ray_plane_intersection(
    *,
    origin: tuple[float, float, float],
    direction: tuple[float, float, float],
    plane_point: tuple[float, float, float],
    plane_normal: tuple[float, float, float],
) -> tuple[float, float, float]:
    """Return the intersection between a ray and a plane.

    Parameters
    ----------
    origin
        World-space ray origin.
    direction
        Unit or non-unit ray direction.
    plane_point
        Any world-space point on the plane.
    plane_normal
        Plane normal direction.

    Returns
    -------
    tuple[float, float, float]
        World-space ray-plane intersection point.
    """

    denominator = sum(direction[index] * plane_normal[index] for index in range(3))
    if abs(denominator) < 1e-9:
        raise ValueError("Ray is parallel to mirror plane.")
    distance = (
        sum(
            (plane_point[index] - origin[index]) * plane_normal[index]
            for index in range(3)
        )
        / denominator
    )
    return tuple(origin[index] + (distance * direction[index]) for index in range(3))


def _mirror_face_point_at_y(
    center: tuple[float, float, float],
    *,
    yaw_deg: float,
    offset_mm: float,
    y_mm: float,
) -> tuple[float, float, float]:
    """Return a point on the visible mirror face at a requested Y row.

    Parameters
    ----------
    center
        Optical center of the mirror mount.
    yaw_deg
        Mirror mount yaw in degrees.
    offset_mm
        Offset from mount center to the visible mirror face along local
        negative X.
    y_mm
        Desired world-space Y coordinate.

    Returns
    -------
    tuple[float, float, float]
        World-space point on the mirror face.
    """

    yaw_rad = math.radians(yaw_deg)
    normal_x = math.cos(yaw_rad)
    normal_y = math.sin(yaw_rad)
    if abs(normal_x) < 1e-9:
        raise ValueError("Mirror face cannot be solved at fixed Y for this yaw.")
    x_mm = center[0] + ((-offset_mm - (normal_y * (y_mm - center[1]))) / normal_x)
    return (x_mm, y_mm, center[2])


def _mirror_face_point_at_x(
    center: tuple[float, float, float],
    *,
    yaw_deg: float,
    offset_mm: float,
    x_mm: float,
) -> tuple[float, float, float]:
    """Return a point on the visible mirror face at a requested X column.

    Parameters
    ----------
    center
        Optical center of the mirror mount.
    yaw_deg
        Mirror mount yaw in degrees.
    offset_mm
        Offset from mount center to the visible mirror face along local
        negative X.
    x_mm
        Desired world-space X coordinate.

    Returns
    -------
    tuple[float, float, float]
        World-space point on the mirror face.
    """

    yaw_rad = math.radians(yaw_deg)
    normal_x = math.cos(yaw_rad)
    normal_y = math.sin(yaw_rad)
    if abs(normal_y) < 1e-9:
        raise ValueError("Mirror face cannot be solved at fixed X for this yaw.")
    y_mm = center[1] + ((-offset_mm - (normal_x * (x_mm - center[0]))) / normal_y)
    return (x_mm, y_mm, center[2])


def _beam_path_points(params: Mapping[str, Any]) -> tuple[BeamPathPoint, ...]:
    """Return named beam path anchors for the Z-fold display.

    Parameters
    ----------
    params
        Scene parameter mapping.

    Returns
    -------
    tuple[BeamPathPoint, ...]
        Source, mirror-surface, and downstream beam path anchors.
    """

    return _trace_z_fold_ray(params)


def _trace_z_fold_ray(params: Mapping[str, Any]) -> tuple[BeamPathPoint, ...]:
    """Trace the nominal Z-fold beam path from mirror planes and reflections.

    Parameters
    ----------
    params
        Scene parameter mapping.

    Returns
    -------
    tuple[BeamPathPoint, ...]
        Source, mirror hit, and iris-row exit points.
    """

    trace = _nominal_physical_trace(params)
    if len(trace.segments) < 5:
        raise ValueError("Nominal physical trace did not reach the iris row.")
    source = trace.segments[0].start_xyz_mm
    m1_surface = trace.interactions[0].point_xyz_mm
    m2_surface = trace.interactions[1].point_xyz_mm
    iris_exit = trace.segments[-1].end_xyz_mm
    return (
        BeamPathPoint(name="source", xyz=source),
        BeamPathPoint(name="m1_surface", xyz=m1_surface),
        BeamPathPoint(name="m2_surface", xyz=m2_surface),
        BeamPathPoint(name="iris_row_exit", xyz=iris_exit),
    )


def _nominal_source_ray(params: Mapping[str, Any]) -> Ray3D:
    """Return the incoming ray for the nominal walking-beam fold.

    Parameters
    ----------
    params
        Scene parameter mapping.

    Returns
    -------
    Ray3D
        Incoming laser ray that reaches the first steering mirror.
    """

    centers = _component_centers(params)
    source_to_m1_mm = float(params["hole_grid_spacing_mm"]) * 2.0
    return Ray3D(
        origin_xyz_mm=(
            centers["m1"][0] - source_to_m1_mm,
            centers["m1"][1],
            centers["m1"][2],
        ),
        direction_xyz=(1.0, 0.0, 0.0),
        beam_radius_mm=float(params["beam_diameter_mm"]) / 2.0,
        wavelength_nm=float(params["wavelength_nm"]),
    )


def _physical_mirror(params: Mapping[str, Any], component_name: str) -> PlaneMirror:
    """Return a finite plane mirror derived from scene component geometry.

    Parameters
    ----------
    params
        Scene parameter mapping.
    component_name
        Component key, either ``m1`` or ``m2``.

    Returns
    -------
    PlaneMirror
        Physical mirror used by import-safe ray tracing.
    """

    if component_name not in {"m1", "m2"}:
        raise ValueError(f"Unsupported mirror component {component_name!r}")
    yaw_key = f"{component_name}_yaw_deg"
    centers = _component_centers(params)
    return PlaneMirror(
        name=component_name.upper(),
        center_xyz_mm=centers[component_name],
        normal_xyz=_mirror_reflective_normal(float(params[yaw_key])),
        clear_radius_mm=KM100CP_MOUNT.clear_aperture_mm / 2.0,
    )


def _physical_iris(params: Mapping[str, Any], component_name: str) -> CircularAperture:
    """Return a finite circular aperture derived from scene geometry.

    Parameters
    ----------
    params
        Scene parameter mapping.
    component_name
        Component key, either ``iris_1`` or ``iris_2``.

    Returns
    -------
    CircularAperture
        Physical aperture used by import-safe ray tracing.
    """

    if component_name not in {"iris_1", "iris_2"}:
        raise ValueError(f"Unsupported iris component {component_name!r}")
    centers = _component_centers(params)
    label = "Iris 1" if component_name == "iris_1" else "Iris 2"
    return CircularAperture(
        name=label,
        center_xyz_mm=centers[component_name],
        normal_xyz=(-1.0, 0.0, 0.0),
        aperture_radius_mm=float(params["alignment_aperture_diameter_mm"]) / 2.0,
        body_radius_mm=ID25_IRIS.outer_diameter_mm / 2.0,
    )


def _nominal_physical_trace(params: Mapping[str, Any]) -> RayTraceResult:
    """Trace the nominal aligned beam through finite scene elements.

    Parameters
    ----------
    params
        Scene parameter mapping.

    Returns
    -------
    RayTraceResult
        Ordered physical trace through M1, M2, Iris 1, and Iris 2.
    """

    return trace_two_mirror_two_iris_system(
        source_ray=_nominal_source_ray(params),
        m1=_physical_mirror(params, "m1"),
        m2=_physical_mirror(params, "m2"),
        iris1=_physical_iris(params, "iris_1"),
        iris2=_physical_iris(params, "iris_2"),
        downstream_length_mm=1.5 * float(params["hole_grid_spacing_mm"]),
    )


def _mirror_adjustments_for_state(
    model: BeamWalkingModel, state: BeamWalkingState
) -> tuple[MirrorAdjustment, MirrorAdjustment]:
    """Return physical mirror adjustments for a storyboard state.

    Parameters
    ----------
    model
        Beam-walking model used for the storyboard.
    state
        Storyboard state to convert.

    Returns
    -------
    tuple[MirrorAdjustment, MirrorAdjustment]
        M1 and M2 physical mirror adjustments.
    """

    aligned = exact_alignment_state(model, name="aligned_reference", frame=state.frame)
    return (
        MirrorAdjustment(
            yaw_mrad=state.horizontal.m1_offset_mm - aligned.horizontal.m1_offset_mm,
            pitch_mrad=state.vertical.m1_offset_mm - aligned.vertical.m1_offset_mm,
        ),
        MirrorAdjustment(
            yaw_mrad=(state.horizontal.m2_angle_mrad - aligned.horizontal.m2_angle_mrad)
            / 2.0,
            pitch_mrad=(state.vertical.m2_angle_mrad - aligned.vertical.m2_angle_mrad)
            / 2.0,
        ),
    )


def _physical_trace_for_state(
    params: Mapping[str, Any],
    model: BeamWalkingModel,
    state: BeamWalkingState,
) -> RayTraceResult:
    """Trace one storyboard state through finite scene elements.

    Parameters
    ----------
    params
        Scene parameter mapping.
    model
        Beam-walking model used for the storyboard.
    state
        Storyboard state to trace.

    Returns
    -------
    RayTraceResult
        Physical trace for the supplied state.
    """

    m1_adjustment, m2_adjustment = _mirror_adjustments_for_state(model, state)
    return trace_two_mirror_two_iris_system(
        source_ray=_nominal_source_ray(params),
        m1=adjusted_plane_mirror(
            _physical_mirror(params, "m1"),
            adjustment=m1_adjustment,
        ),
        m2=adjusted_plane_mirror(
            _physical_mirror(params, "m2"),
            adjustment=m2_adjustment,
        ),
        iris1=_physical_iris(params, "iris_1"),
        iris2=_physical_iris(params, "iris_2"),
        downstream_length_mm=1.5 * float(params["hole_grid_spacing_mm"]),
    )


def _interaction_point_or_center(
    trace: RayTraceResult,
    *,
    element_name: str,
    fallback_xyz: tuple[float, float, float],
) -> tuple[float, float, float]:
    """Return an interaction point when present, otherwise a fallback center.

    Parameters
    ----------
    trace
        Physical trace to inspect.
    element_name
        Interaction element name.
    fallback_xyz
        Point used when the trace stopped before the element.

    Returns
    -------
    tuple[float, float, float]
        Interaction point or fallback point.
    """

    for interaction in trace.interactions:
        if interaction.element_name == element_name:
            return interaction.point_xyz_mm
    return fallback_xyz


def _blocked_at_key(trace: RayTraceResult) -> str:
    """Return the scene-local blocking key for a physical trace.

    Parameters
    ----------
    trace
        Physical trace to inspect.

    Returns
    -------
    str
        Empty string when unblocked, otherwise a scene-local element key.
    """

    return {
        "": "",
        "M1": "m1",
        "M2": "m2",
        "Iris 1": "iris_1",
        "Iris 2": "iris_2",
    }.get(trace.blocked_at, trace.blocked_at)


def _walking_beam_model(params: Mapping[str, Any]) -> BeamWalkingModel:
    """Create the import-safe beam-walking model from scene defaults.

    Parameters
    ----------
    params
        Scene parameter mapping.

    Returns
    -------
    BeamWalkingModel
        Two-axis beam-walking model.
    """

    centers = _component_centers(params)
    m2_x = centers["m2"][0]
    return BeamWalkingModel(
        iris1_distance_mm=centers["iris_1"][0] - m2_x,
        iris2_distance_mm=centers["iris_2"][0] - m2_x,
        iris_radius_mm=float(params["alignment_aperture_diameter_mm"]) / 2.0,
        horizontal=BeamWalkingAxisModel(
            initial_offset_mm=float(params["initial_horizontal_offset_mm"]),
            initial_angle_mrad=float(params["initial_horizontal_angle_mrad"]),
        ),
        vertical=BeamWalkingAxisModel(
            initial_offset_mm=float(params["initial_vertical_offset_mm"]),
            initial_angle_mrad=float(params["initial_vertical_angle_mrad"]),
        ),
    )


def _alignment_states(params: Mapping[str, Any]) -> tuple[BeamWalkingState, ...]:
    """Create the explicit walking-beam alignment states.

    Parameters
    ----------
    params
        Scene parameter mapping.

    Returns
    -------
    tuple[BeamWalkingState, ...]
        Ordered storyboard states.
    """

    return iterative_alignment_sequence(
        _walking_beam_model(params),
        frames=(
            int(params["frame_start"]),
            int(params["frame_m1_centers_iris1"]),
            int(params["frame_m2_centers_iris2"]),
            int(params["frame_m1_refinement"]),
            int(params["frame_m2_refinement"]),
            int(params["frame_end"]),
        ),
    )


def _storyboard_captions_for_states(
    params: Mapping[str, Any], states: tuple[BeamWalkingState, ...]
) -> tuple[StoryboardCaption, ...]:
    """Return one caption for each storyboard alignment state.

    Parameters
    ----------
    params
        Scene parameter mapping.
    states
        Ordered alignment states in the storyboard.

    Returns
    -------
    tuple[StoryboardCaption, ...]
        Caption records aligned with the supplied states.
    """

    caption_texts = params["storyboard_captions"]
    return tuple(
        StoryboardCaption(
            state_name=state.name,
            frame=state.frame,
            text=str(caption_texts[state.name]),
        )
        for state in states
    )


def _label_style(params: Mapping[str, Any]) -> LabelStyle:
    """Return the scene-local label material style.

    Parameters
    ----------
    params
        Scene parameter mapping.

    Returns
    -------
    LabelStyle
        Color and emission settings for scene labels.
    """

    red, green, blue, alpha = params["label_color"]
    return LabelStyle(
        color=(float(red), float(green), float(blue), float(alpha)),
        emission_strength=float(params["label_emission_strength"]),
    )


def _set_material_input_if_present(material: Any, input_name: str, value: Any) -> None:
    """Set one Principled BSDF input when the Blender runtime exposes it.

    Parameters
    ----------
    material
        Blender material whose shader node should be updated.
    input_name
        Name of the Principled BSDF input.
    value
        Value assigned to the input when it exists.
    """

    bsdf = material.node_tree.nodes.get("Principled BSDF")
    if bsdf is not None and input_name in bsdf.inputs:
        bsdf.inputs[input_name].default_value = value


def _apply_label_style(materials: Mapping[str, Any], style: LabelStyle) -> None:
    """Apply scene-local label styling to the generated material palette.

    Parameters
    ----------
    materials
        Material palette returned by ``create_materials``.
    style
        Scene-local label color and emission settings.
    """

    label = materials["label"]
    label.diffuse_color = style.color
    _set_material_input_if_present(label, "Base Color", style.color)
    _set_material_input_if_present(label, "Alpha", style.color[3])
    _set_material_input_if_present(label, "Emission Color", style.color)
    _set_material_input_if_present(label, "Emission Strength", style.emission_strength)


def _beam_visual_radius(params: Mapping[str, Any]) -> float:
    """Return the rendered beam radius without changing physical beam math.

    Parameters
    ----------
    params
        Scene parameter mapping.

    Returns
    -------
    float
        Rendered beam radius in millimeters.
    """

    return float(params["beam_visual_diameter_mm"]) / 2.0


def _iris_spot_radius(params: Mapping[str, Any]) -> float:
    """Return the rendered iris spot radius.

    Parameters
    ----------
    params
        Scene parameter mapping.

    Returns
    -------
    float
        Rendered spot radius in millimeters.
    """

    return float(params["iris_spot_radius_mm"])


def _lerp_transverse_at_x(
    *,
    x_mm: float,
    x1_mm: float,
    y1_mm: float,
    z1_mm: float,
    x2_mm: float,
    y2_mm: float,
    z2_mm: float,
) -> tuple[float, float]:
    """Linearly interpolate or extrapolate transverse beam coordinates.

    Parameters
    ----------
    x_mm
        X coordinate where the transverse coordinates are requested.
    x1_mm
        First reference X coordinate.
    y1_mm
        First reference Y coordinate.
    z1_mm
        First reference Z coordinate.
    x2_mm
        Second reference X coordinate.
    y2_mm
        Second reference Y coordinate.
    z2_mm
        Second reference Z coordinate.

    Returns
    -------
    tuple[float, float]
        Interpolated Y and Z coordinates.
    """

    denominator = x2_mm - x1_mm
    if abs(denominator) < 1e-9:
        raise ValueError("Reference X coordinates must be distinct.")
    fraction = (x_mm - x1_mm) / denominator
    return (
        y1_mm + ((y2_mm - y1_mm) * fraction),
        z1_mm + ((z2_mm - z1_mm) * fraction),
    )


def _downstream_beam_path_for_state(
    params: Mapping[str, Any],
    model: BeamWalkingModel,
    state: BeamWalkingState,
) -> DownstreamBeamPath:
    """Return animated downstream beam points for one alignment state.

    Parameters
    ----------
    params
        Scene parameter mapping.
    model
        Beam-walking model used to compute iris intercepts.
    state
        Alignment state to display.

    Returns
    -------
    DownstreamBeamPath
        Beam start, iris intercepts, and downstream exit point.
    """

    centers = _component_centers(params)
    trace = _physical_trace_for_state(params, model, state)
    interactions_by_name = {
        interaction.element_name: interaction for interaction in trace.interactions
    }
    if len(trace.segments) >= 3:
        start_xyz = trace.segments[2].start_xyz_mm
        beam_visible = True
    else:
        start_xyz = trace.segments[-1].start_xyz_mm
        beam_visible = False

    iris1_xyz = _interaction_point_or_center(
        trace,
        element_name="Iris 1",
        fallback_xyz=centers["iris_1"],
    )
    iris2_xyz = _interaction_point_or_center(
        trace,
        element_name="Iris 2",
        fallback_xyz=centers["iris_2"],
    )
    exit_xyz = trace.segments[-1].end_xyz_mm
    visible_end_xyz = trace.segments[-1].end_xyz_mm
    blocked_at = _blocked_at_key(trace)

    return DownstreamBeamPath(
        start_xyz=start_xyz,
        iris1_xyz=iris1_xyz,
        iris2_xyz=iris2_xyz,
        exit_xyz=exit_xyz,
        visible_end_xyz=visible_end_xyz,
        blocked_at=blocked_at,
        beam_visible=beam_visible,
        iris1_visible="Iris 1" in interactions_by_name,
        iris2_visible="Iris 2" in interactions_by_name,
    )


def _iris_spot_visibility(path: DownstreamBeamPath) -> tuple[bool, bool]:
    """Return visible spot flags for Iris 1 and Iris 2.

    Parameters
    ----------
    path
        Downstream beam path with physical blocking status.

    Returns
    -------
    tuple[bool, bool]
        Visibility for Iris 1 and Iris 2 readout spots.
    """

    return (path.iris1_visible, path.iris2_visible)


def _iris_spot_offsets_for_path(
    params: Mapping[str, Any], path: DownstreamBeamPath
) -> BeamIntercepts:
    """Return display spot offsets derived from traced iris points.

    Parameters
    ----------
    params
        Scene parameter mapping.
    path
        Trace-derived downstream beam path.

    Returns
    -------
    BeamIntercepts
        Display-scaled transverse offsets for the two iris cards.
    """

    centers = _component_centers(params)
    exaggeration = float(params["spot_display_exaggeration"])
    return BeamIntercepts(
        iris1=IrisOffset(
            y_mm=(path.iris1_xyz[1] - centers["iris_1"][1]) * exaggeration,
            z_mm=(path.iris1_xyz[2] - centers["iris_1"][2]) * exaggeration,
        ),
        iris2=IrisOffset(
            y_mm=(path.iris2_xyz[1] - centers["iris_2"][1]) * exaggeration,
            z_mm=(path.iris2_xyz[2] - centers["iris_2"][2]) * exaggeration,
        ),
    )


def _folded_beam_path_for_state(
    params: Mapping[str, Any],
    model: BeamWalkingModel,
    state: BeamWalkingState,
) -> BeamSegmentPath:
    """Return the animated M1-to-M2 beam segment for one alignment state.

    Parameters
    ----------
    params
        Scene parameter mapping.
    model
        Beam-walking model used to compute the shared M2 hit point.
    state
        Alignment state to display.

    Returns
    -------
    BeamSegmentPath
        Beam segment from M1's visible surface to the same M2 point used by
        the downstream beam.
    """

    trace = _physical_trace_for_state(params, model, state)
    if len(trace.segments) >= 2:
        segment = trace.segments[1]
    else:
        segment = trace.segments[0]
    return BeamSegmentPath(
        start_xyz=segment.start_xyz_mm,
        end_xyz=segment.end_xyz_mm,
    )


def _iris_closeup_camera_pose(params: Mapping[str, Any]) -> CameraPose:
    """Return a close-up camera pose that frames both irises.

    Parameters
    ----------
    params
        Scene parameter mapping.

    Returns
    -------
    CameraPose
        Camera location, target, and lens length.
    """

    centers = _component_centers(params)
    midpoint_x = (centers["iris_1"][0] + centers["iris_2"][0]) / 2.0
    axis_z = float(params["optical_axis_z_mm"])
    return CameraPose(
        location_xyz=(
            midpoint_x,
            -float(params["iris_closeup_distance_y_mm"]),
            axis_z + float(params["iris_closeup_elevation_mm"]),
        ),
        target_xyz=(midpoint_x, 0.0, axis_z),
        lens_mm=float(params["iris_closeup_lens_mm"]),
    )


def _wide_camera_plan(params: Mapping[str, Any]) -> WideCameraPlan:
    """Return a wide camera plan that keeps the full layout in frame.

    Parameters
    ----------
    params
        Scene parameter mapping.

    Returns
    -------
    WideCameraPlan
        Animated wide-camera target, distance, and elevation values.
    """

    centers = _component_centers(params)
    midpoint_x = (centers["m1"][0] + centers["iris_2"][0]) / 2.0
    axis_z = float(params["optical_axis_z_mm"])
    target = (midpoint_x, -5.0, axis_z + 6.0)
    return WideCameraPlan(
        target_xyz=target,
        distance_mm=float(params["wide_camera_distance_mm"]),
        elevation_mm=float(params["wide_camera_elevation_mm"]),
        end_target_xyz=target,
        end_distance_mm=float(params["wide_camera_end_distance_mm"]),
        end_elevation_mm=float(params["wide_camera_end_elevation_mm"]),
    )


def _create_iris_closeup_camera(
    *,
    name: str,
    pose: CameraPose,
) -> Any:
    """Create a camera looking down the iris row.

    Parameters
    ----------
    name
        Camera object name.
    pose
        Camera pose returned by ``_iris_closeup_camera_pose``.

    Returns
    -------
    object
        Blender camera object.
    """

    from mathutils import Vector  # pyright: ignore[reportMissingImports]

    from simulations.blender.altair_blender.scene import get_bpy

    bpy = get_bpy()
    target = Vector(pose.target_xyz)
    bpy.ops.object.camera_add(location=pose.location_xyz)
    camera = bpy.context.object
    camera.name = name
    direction = target - camera.location
    camera.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    camera.data.lens = pose.lens_mm
    camera.data.dof.use_dof = True
    camera.data.dof.focus_distance = direction.length
    return camera


def main(output_path: str | None = None) -> None:
    """Generate the walking-beam alignment teaching scene.

    Parameters
    ----------
    output_path
        Optional path where the generated ``.blend`` file should be saved.
    """

    _ensure_repo_root_on_path()

    from simulations.blender.altair_blender.animation import (
        keyframe_transform,
        set_linear_interpolation,
    )
    from simulations.blender.altair_blender.cameras import (
        create_hero_camera,
        create_wide_camera,
    )
    from simulations.blender.altair_blender.geometry import (
        create_kinematic_mirror_mount,
        create_optical_table,
        create_post_mounted_iris,
        create_scene_label,
        create_studio_backdrop,
    )
    from simulations.blender.altair_blender.materials import create_materials
    from simulations.blender.altair_blender.optics import (
        SpotOffset,
        create_beam_between,
        create_return_spot,
        set_beam_between,
        validate_positive,
    )
    from simulations.blender.altair_blender.scene import (
        add_area_light,
        configure_cycles_device,
        configure_scene,
        ensure_collection,
        get_bpy,
        reset_scene,
        validate_output_path,
    )

    params = DEFAULT_PARAMETERS
    validate_positive("beam_diameter_mm", params["beam_diameter_mm"])
    validate_positive("beam_visual_diameter_mm", params["beam_visual_diameter_mm"])
    validate_positive(
        "alignment_aperture_diameter_mm", params["alignment_aperture_diameter_mm"]
    )
    validate_positive("iris_spot_radius_mm", params["iris_spot_radius_mm"])
    validate_positive("iris_display_aperture_mm", params["iris_display_aperture_mm"])
    validate_positive("iris_reticle_radius_mm", params["iris_reticle_radius_mm"])
    validate_positive("label_emission_strength", params["label_emission_strength"])
    validate_positive(
        "storyboard_caption_size_mm", params["storyboard_caption_size_mm"]
    )
    validate_positive("hole_grid_spacing_mm", params["hole_grid_spacing_mm"])

    bpy = get_bpy()
    reset_scene()
    configure_scene(
        frame_start=int(params["frame_start"]),
        frame_end=int(params["frame_end"]),
        fps=24,
        render_preset=os.environ.get(
            "RENDER_MODE", str(params["default_render_preset"])
        ),
    )
    cycles_device = os.environ.get("CYCLES_DEVICE", "").strip()
    if cycles_device:
        configure_cycles_device(cycles_device)

    collection = ensure_collection("Walking Beam Alignment")
    materials = create_materials()
    _apply_label_style(materials, _label_style(params))
    centers = _component_centers(params)
    beam_path = _beam_path_points(params)
    model = _walking_beam_model(params)
    states = _alignment_states(params)
    axis_z = float(params["optical_axis_z_mm"])
    table_top_z = float(params["table_top_z_mm"])
    beam_radius = _beam_visual_radius(params)
    iris_spot_radius = _iris_spot_radius(params)

    create_optical_table(
        collection=collection,
        materials=materials,
        length_mm=float(params["table_length_mm"]),
        width_mm=float(params["table_width_mm"]),
        center_x_mm=float(params["table_center_x_mm"]),
        center_y_mm=float(params["table_center_y_mm"]),
        center_z_mm=float(params["table_center_z_mm"]),
    )
    create_studio_backdrop(
        collection=collection,
        materials=materials,
        center_x_mm=10.0,
        y_mm=70.0,
        center_z_mm=42.0,
    )
    add_area_light(
        name="Walking Beam Softbox",
        location=(-5.0, -92.0, 128.0),
        power=float(params["softbox_power"]),
        size=float(params["softbox_size_mm"]),
    )
    add_area_light(
        name="Iris Row Fill",
        location=(70.0, -42.0, 80.0),
        power=float(params["fill_power"]),
        size=36.0,
    )
    add_area_light(
        name="Mirror Edge Rim",
        location=(-118.0, 42.0, 82.0),
        power=float(params["rim_light_power"]),
        size=30.0,
    )

    m1 = create_kinematic_mirror_mount(
        collection=collection,
        materials=materials,
        x_mm=centers["m1"][0],
        y_mm=centers["m1"][1],
        optical_axis_z_mm=axis_z,
        yaw_deg=float(params["m1_yaw_deg"]),
        table_top_z_mm=table_top_z,
        name="M1 KM100CP-Style Mount",
    )
    m2 = create_kinematic_mirror_mount(
        collection=collection,
        materials=materials,
        x_mm=centers["m2"][0],
        y_mm=centers["m2"][1],
        optical_axis_z_mm=axis_z,
        yaw_deg=float(params["m2_yaw_deg"]),
        table_top_z_mm=table_top_z,
        name="M2 KM100CP-Style Mount",
    )
    create_post_mounted_iris(
        collection=collection,
        materials=materials,
        x_mm=centers["iris_1"][0],
        y_mm=centers["iris_1"][1],
        optical_axis_z_mm=axis_z,
        display_aperture_mm=float(params["iris_display_aperture_mm"]),
        reticle_radius_mm=float(params["iris_reticle_radius_mm"]),
        reticle_faces=str(params["iris_reticle_faces"]),
        table_top_z_mm=table_top_z,
        name="Iris 1 ID25-Style Assembly",
    )
    create_post_mounted_iris(
        collection=collection,
        materials=materials,
        x_mm=centers["iris_2"][0],
        y_mm=centers["iris_2"][1],
        optical_axis_z_mm=axis_z,
        display_aperture_mm=float(params["iris_display_aperture_mm"]),
        reticle_radius_mm=float(params["iris_reticle_radius_mm"]),
        reticle_faces=str(params["iris_reticle_faces"]),
        table_top_z_mm=table_top_z,
        name="Iris 2 ID25-Style Assembly",
    )

    create_beam_between(
        name="Incoming 561 nm Beam",
        start_xyz=beam_path[0].xyz,
        end_xyz=beam_path[1].xyz,
        radius_mm=beam_radius,
        material=materials["laser"],
        collection=collection,
    )
    first_folded_path = _folded_beam_path_for_state(params, model, states[0])
    first_downstream_path = _downstream_beam_path_for_state(params, model, states[0])
    first_display = _iris_spot_offsets_for_path(params, first_downstream_path)
    folded_beam = create_beam_between(
        name="Animated M1 to M2 Beam",
        start_xyz=first_folded_path.start_xyz,
        end_xyz=first_folded_path.end_xyz,
        radius_mm=beam_radius,
        material=materials["laser"],
        collection=collection,
    )
    final_beam = create_beam_between(
        name="Animated Beam After M2",
        start_xyz=first_downstream_path.start_xyz,
        end_xyz=first_downstream_path.visible_end_xyz,
        radius_mm=beam_radius,
        material=materials["laser"],
        collection=collection,
    )
    spot1 = create_return_spot(
        name="Iris 1 Beam Spot",
        card_x_mm=centers["iris_1"][0],
        offset=SpotOffset(
            y_mm=first_display.iris1.y_mm,
            z_mm=first_display.iris1.z_mm,
        ),
        radius_mm=iris_spot_radius,
        material=materials["spot_a"],
        collection=collection,
        optical_axis_z_mm=axis_z,
    )
    spot2 = create_return_spot(
        name="Iris 2 Beam Spot",
        card_x_mm=centers["iris_2"][0],
        offset=SpotOffset(
            y_mm=first_display.iris2.y_mm,
            z_mm=first_display.iris2.z_mm,
        ),
        radius_mm=iris_spot_radius,
        material=materials["spot_b"],
        collection=collection,
        optical_axis_z_mm=axis_z,
    )

    for state in states:
        folded_path = _folded_beam_path_for_state(params, model, state)
        downstream_path = _downstream_beam_path_for_state(params, model, state)
        set_beam_between(
            beam=folded_beam,
            start_xyz=folded_path.start_xyz,
            end_xyz=folded_path.end_xyz,
        )
        folded_beam.keyframe_insert(data_path="location", frame=state.frame)
        folded_beam.keyframe_insert(data_path="rotation_euler", frame=state.frame)
        folded_beam.keyframe_insert(data_path="scale", frame=state.frame)
        set_beam_between(
            beam=final_beam,
            start_xyz=downstream_path.start_xyz,
            end_xyz=downstream_path.visible_end_xyz,
        )
        final_beam.hide_viewport = not downstream_path.beam_visible
        final_beam.hide_render = not downstream_path.beam_visible
        final_beam.keyframe_insert(data_path="location", frame=state.frame)
        final_beam.keyframe_insert(data_path="rotation_euler", frame=state.frame)
        final_beam.keyframe_insert(data_path="scale", frame=state.frame)
        final_beam.keyframe_insert(data_path="hide_viewport", frame=state.frame)
        final_beam.keyframe_insert(data_path="hide_render", frame=state.frame)
        spot1_visible, spot2_visible = _iris_spot_visibility(downstream_path)
        spot1.hide_viewport = not spot1_visible
        spot1.hide_render = not spot1_visible
        spot2.hide_viewport = not spot2_visible
        spot2.hide_render = not spot2_visible
        for spot in (spot1, spot2):
            spot.keyframe_insert(data_path="hide_viewport", frame=state.frame)
            spot.keyframe_insert(data_path="hide_render", frame=state.frame)

        display = _iris_spot_offsets_for_path(params, downstream_path)
        spot1.location = (
            centers["iris_1"][0] - 0.9,
            centers["iris_1"][1] + display.iris1.y_mm,
            axis_z + display.iris1.z_mm,
        )
        spot2.location = (
            centers["iris_2"][0] - 0.9,
            centers["iris_2"][1] + display.iris2.y_mm,
            axis_z + display.iris2.z_mm,
        )
        spot1.keyframe_insert(data_path="location", frame=state.frame)
        spot2.keyframe_insert(data_path="location", frame=state.frame)

        mirror_scale = float(params["mirror_display_exaggeration"])
        keyframe_transform(
            m1,
            frame=state.frame,
            rotation_euler=(
                math.radians(state.vertical.m1_offset_mm * mirror_scale),
                0.0,
                math.radians(
                    float(params["m1_yaw_deg"])
                    + (state.horizontal.m1_offset_mm * mirror_scale)
                ),
            ),
        )
        keyframe_transform(
            m2,
            frame=state.frame,
            rotation_euler=(
                math.radians(state.vertical.m2_angle_mrad * mirror_scale * 0.05),
                0.0,
                math.radians(
                    float(params["m2_yaw_deg"])
                    + (state.horizontal.m2_angle_mrad * mirror_scale * 0.05)
                ),
            ),
        )

    for obj in (m1, m2, spot1, spot2, folded_beam, final_beam):
        set_linear_interpolation(obj)

    if params["show_minimal_labels"]:
        m1_label, m2_label, iris1_label, iris2_label, height_label = params[
            "scene_labels"
        ]
        create_scene_label(
            collection=collection,
            materials=materials,
            name="Label M1",
            text=m1_label,
            location=(centers["m1"][0] - 12.0, centers["m1"][1] - 20.0, axis_z + 30.0),
            size_mm=2.5,
        )
        create_scene_label(
            collection=collection,
            materials=materials,
            name="Label M2",
            text=m2_label,
            location=(centers["m2"][0] - 15.0, centers["m2"][1] + 18.0, axis_z + 30.0),
            size_mm=2.5,
        )
        create_scene_label(
            collection=collection,
            materials=materials,
            name="Label Iris 1",
            text=iris1_label,
            location=(centers["iris_1"][0], -32.0, axis_z + 26.0),
            size_mm=2.2,
        )
        create_scene_label(
            collection=collection,
            materials=materials,
            name="Label Iris 2",
            text=iris2_label,
            location=(centers["iris_2"][0], -32.0, axis_z + 26.0),
            size_mm=2.2,
        )
        create_scene_label(
            collection=collection,
            materials=materials,
            name="Label Same Height",
            text=height_label,
            location=(
                (centers["iris_1"][0] + centers["iris_2"][0]) / 2.0,
                -34.0,
                axis_z - 22.0,
            ),
            size_mm=1.8,
        )

    if params["show_storyboard_captions"]:
        caption_location = tuple(
            float(component) for component in params["storyboard_caption_location_mm"]
        )
        caption_size = float(params["storyboard_caption_size_mm"])
        caption_objects = {
            caption.state_name: create_scene_label(
                collection=collection,
                materials=materials,
                name=f"Storyboard Caption {caption.state_name}",
                text=caption.text,
                location=caption_location,
                size_mm=caption_size,
            )
            for caption in _storyboard_captions_for_states(params, states)
        }
        for active_caption in _storyboard_captions_for_states(params, states):
            for state_name, caption_obj in caption_objects.items():
                hidden = state_name != active_caption.state_name
                caption_obj.hide_viewport = hidden
                caption_obj.hide_render = hidden
                caption_obj.keyframe_insert(
                    data_path="hide_viewport", frame=active_caption.frame
                )
                caption_obj.keyframe_insert(
                    data_path="hide_render", frame=active_caption.frame
                )

    wide_plan = _wide_camera_plan(params)
    create_wide_camera(
        target=wide_plan.target_xyz,
        distance_mm=wide_plan.distance_mm,
        elevation_mm=wide_plan.elevation_mm,
        frame_start=int(params["frame_start"]),
        frame_end=int(params["frame_end"]),
        end_target=wide_plan.end_target_xyz,
        end_distance_mm=wide_plan.end_distance_mm,
        end_elevation_mm=wide_plan.end_elevation_mm,
    )
    _create_iris_closeup_camera(
        name=str(params["iris_closeup_camera_name"]),
        pose=_iris_closeup_camera_pose(params),
    )
    create_hero_camera(
        target=(38.0, -4.0, axis_z + 4.0),
        frame_start=int(params["frame_start"]),
        frame_end=int(params["frame_end"]),
        focus_distance_mm=235.0,
    )

    output = validate_output_path(output_path)
    if output is not None:
        bpy.ops.wm.save_as_mainfile(filepath=str(output))


if __name__ == "__main__":
    main(_parse_output_path(sys.argv))
