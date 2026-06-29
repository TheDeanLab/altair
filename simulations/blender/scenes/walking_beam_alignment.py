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
    BeamWalkingModel,
    BeamWalkingState,
    BeamWalkingAxisModel,
    compute_beam_intercepts,
    iterative_alignment_sequence,
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


DEFAULT_PARAMETERS: dict[str, Any] = {
    "wavelength_nm": 561.0,
    "beam_diameter_mm": 1.0,
    "alignment_aperture_diameter_mm": 2.5,
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
    "spot_display_exaggeration": 2.0,
    "mirror_display_exaggeration": 0.18,
    "iris_source": ID25_IRIS.source_notes,
    "post_holder_source": PH2_POST_HOLDER.source_notes,
    "post_source": TR15_POST.source_notes,
    "mirror_mount_source": KM100CP_MOUNT.source_notes,
    "show_minimal_labels": True,
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
    "m1_yaw_deg": 225.0,
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


def _mirror_surface_point(
    center: tuple[float, float, float], *, yaw_deg: float, offset_mm: float
) -> tuple[float, float, float]:
    """Return the displayed reflective surface point for a mirror mount.

    Parameters
    ----------
    center
        Optical center of the mirror mount.
    yaw_deg
        Mirror mount yaw in degrees.
    offset_mm
        Offset from mount center to the visible mirror surface.

    Returns
    -------
    tuple[float, float, float]
        World-space point on the mirror surface.
    """

    yaw_rad = math.radians(yaw_deg)
    return (
        center[0] + (math.cos(yaw_rad) * offset_mm),
        center[1] + (math.sin(yaw_rad) * offset_mm),
        center[2],
    )


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

    centers = _component_centers(params)
    offset = float(params["mirror_surface_offset_mm"])
    m1_surface = _mirror_surface_point(
        centers["m1"],
        yaw_deg=float(params["m1_yaw_deg"]),
        offset_mm=offset,
    )
    m2_surface = _mirror_surface_point(
        centers["m2"],
        yaw_deg=float(params["m2_yaw_deg"]),
        offset_mm=offset,
    )
    iris_exit = (
        centers["iris_2"][0] + (1.5 * float(params["hole_grid_spacing_mm"])),
        centers["iris_2"][1],
        centers["iris_2"][2],
    )
    return (
        BeamPathPoint(
            name="source",
            xyz=(m1_surface[0] - 50.0, m1_surface[1], m1_surface[2]),
        ),
        BeamPathPoint(name="m1_surface", xyz=m1_surface),
        BeamPathPoint(name="m2_surface", xyz=m2_surface),
        BeamPathPoint(name="iris_row_exit", xyz=iris_exit),
    )


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


def _display_intercepts(
    intercepts: BeamIntercepts, *, exaggeration: float
) -> BeamIntercepts:
    """Scale beam offsets for the visible iris readout.

    Parameters
    ----------
    intercepts
        Physical beam offsets at both irises.
    exaggeration
        Visual scale factor.

    Returns
    -------
    BeamIntercepts
        Scaled intercepts for display.
    """

    return BeamIntercepts(
        iris1=type(intercepts.iris1)(
            y_mm=intercepts.iris1.y_mm * exaggeration,
            z_mm=intercepts.iris1.z_mm * exaggeration,
        ),
        iris2=type(intercepts.iris2)(
            y_mm=intercepts.iris2.y_mm * exaggeration,
            z_mm=intercepts.iris2.z_mm * exaggeration,
        ),
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
    validate_positive(
        "alignment_aperture_diameter_mm", params["alignment_aperture_diameter_mm"]
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
    centers = _component_centers(params)
    beam_path = _beam_path_points(params)
    model = _walking_beam_model(params)
    states = _alignment_states(params)
    axis_z = float(params["optical_axis_z_mm"])
    table_top_z = float(params["table_top_z_mm"])
    beam_radius = float(params["beam_diameter_mm"]) / 2.0

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
        table_top_z_mm=table_top_z,
        name="Iris 1 ID25-Style Assembly",
    )
    create_post_mounted_iris(
        collection=collection,
        materials=materials,
        x_mm=centers["iris_2"][0],
        y_mm=centers["iris_2"][1],
        optical_axis_z_mm=axis_z,
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
    create_beam_between(
        name="M1 to M2 Folded Beam",
        start_xyz=beam_path[1].xyz,
        end_xyz=beam_path[2].xyz,
        radius_mm=beam_radius,
        material=materials["laser"],
        collection=collection,
    )
    create_beam_between(
        name="Final Beam Down Iris Row",
        start_xyz=beam_path[2].xyz,
        end_xyz=beam_path[3].xyz,
        radius_mm=beam_radius,
        material=materials["laser"],
        collection=collection,
    )

    first_display = _display_intercepts(
        compute_beam_intercepts(model, states[0]),
        exaggeration=float(params["spot_display_exaggeration"]),
    )
    spot1 = create_return_spot(
        name="Iris 1 Beam Spot",
        card_x_mm=centers["iris_1"][0],
        offset=SpotOffset(
            y_mm=first_display.iris1.y_mm,
            z_mm=first_display.iris1.z_mm,
        ),
        radius_mm=0.85,
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
        radius_mm=0.85,
        material=materials["spot_b"],
        collection=collection,
        optical_axis_z_mm=axis_z,
    )

    for state in states:
        display = _display_intercepts(
            compute_beam_intercepts(model, state),
            exaggeration=float(params["spot_display_exaggeration"]),
        )
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

    for obj in (m1, m2, spot1, spot2):
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
