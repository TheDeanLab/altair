"""Generate the achromat back-reflection alignment teaching scene."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
import math
import os
from pathlib import Path
import sys
from typing import Any, NamedTuple


def _ensure_repo_root_on_path() -> None:
    """Ensure direct script execution can import the repository package."""

    repo_root = Path(__file__).resolve().parents[3]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))


_ensure_repo_root_on_path()

from simulations.blender.altair_blender.prescriptions import (  # noqa: E402
    AC254_100_A,
    LMR1_MOUNT,
    LensSurface,
)
from simulations.blender.altair_blender.optics import (  # noqa: E402
    ReflectedSpotSummary,
    SpotOffset,
    reflect_ray_bundle_from_surface,
)
from simulations.blender.altair_blender.scene import RENDER_PRESETS  # noqa: E402

SCENE_NAME = "achromat_back_reflection"


class AlignmentState(NamedTuple):
    """One ray-traced alignment state in the teaching timeline."""

    name: str
    frame: int
    tilt_y_deg: float
    tilt_z_deg: float
    decenter_y_mm: float
    decenter_z_mm: float


class SpotKeyframe(NamedTuple):
    """Displayed spot position and radius for one timeline keyframe."""

    frame: int
    offset: SpotOffset
    radius_mm: float


DEFAULT_PARAMETERS: dict[str, Any] = {
    "wavelength_nm": 561.0,
    "beam_diameter_mm": 1.0,
    "aperture_diameter_mm": 1.0,
    "lens_focal_length_mm": 100.0,
    "lens_diameter_mm": AC254_100_A.diameter_mm,
    "lens_thickness_mm": AC254_100_A.center_thickness_mm,
    "lens_source": AC254_100_A.source_notes,
    "mount_source": LMR1_MOUNT.source_notes,
    "reflected_surfaces": ("front_bk7_air", "rear_sf5_air"),
    "show_minimal_labels": True,
    "hero_camera_name": "Hero Camera",
    "default_render_preset": "final",
    "render_presets": RENDER_PRESETS,
    "scene_labels": (
        "Aperture card",
        "AC254-100-A doublet",
        "LMR1 mount",
        "Two return reflections",
    ),
    "card_x_mm": 0.0,
    "lens_x_mm": 75.0,
    "optical_axis_z_mm": LMR1_MOUNT.optical_axis_height_mm,
    "initial_tilt_y_deg": 0.28,
    "initial_tilt_z_deg": -0.16,
    "initial_decenter_y_mm": 0.28,
    "initial_decenter_z_mm": -0.18,
    "exaggeration": 5.0,
    "alignment_display_exaggeration": 20.0,
    "frame_start": 1,
    "frame_tilt_corrected": 36,
    "frame_horizontal_decentered": 60,
    "frame_horizontal_corrected": 96,
    "frame_vertical_decentered": 120,
    "frame_vertical_corrected": 156,
    "frame_decenter_corrected": 156,
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


def _alignment_states(params: Mapping[str, Any]) -> tuple[AlignmentState, ...]:
    """Create the explicit alignment sequence used by the animation.

    Parameters
    ----------
    params
        Scene parameter mapping.

    Returns
    -------
    tuple[AlignmentState, ...]
        Ordered states for rotation, horizontal translation, vertical
        translation, and final alignment.
    """

    return (
        AlignmentState(
            name="rotation_error",
            frame=int(params["frame_start"]),
            tilt_y_deg=float(params["initial_tilt_y_deg"]),
            tilt_z_deg=0.0,
            decenter_y_mm=0.0,
            decenter_z_mm=0.0,
        ),
        AlignmentState(
            name="angle_corrected",
            frame=int(params["frame_tilt_corrected"]),
            tilt_y_deg=0.0,
            tilt_z_deg=0.0,
            decenter_y_mm=0.0,
            decenter_z_mm=0.0,
        ),
        AlignmentState(
            name="horizontal_decenter",
            frame=int(params["frame_horizontal_decentered"]),
            tilt_y_deg=0.0,
            tilt_z_deg=0.0,
            decenter_y_mm=float(params["initial_decenter_y_mm"]),
            decenter_z_mm=0.0,
        ),
        AlignmentState(
            name="horizontal_corrected",
            frame=int(params["frame_horizontal_corrected"]),
            tilt_y_deg=0.0,
            tilt_z_deg=0.0,
            decenter_y_mm=0.0,
            decenter_z_mm=0.0,
        ),
        AlignmentState(
            name="vertical_decenter",
            frame=int(params["frame_vertical_decentered"]),
            tilt_y_deg=0.0,
            tilt_z_deg=0.0,
            decenter_y_mm=0.0,
            decenter_z_mm=float(params["initial_decenter_z_mm"]),
        ),
        AlignmentState(
            name="aligned",
            frame=int(params["frame_vertical_corrected"]),
            tilt_y_deg=0.0,
            tilt_z_deg=0.0,
            decenter_y_mm=0.0,
            decenter_z_mm=0.0,
        ),
        AlignmentState(
            name="aligned_hold",
            frame=int(params["frame_end"]),
            tilt_y_deg=0.0,
            tilt_z_deg=0.0,
            decenter_y_mm=0.0,
            decenter_z_mm=0.0,
        ),
    )


def _alignment_display_pose(
    params: Mapping[str, Any],
    state: AlignmentState,
    *,
    lens_x: float,
    axis_z: float,
) -> tuple[tuple[float, float, float], tuple[float, float, float]]:
    """Return the exaggerated lens pose used in the visible alignment animation.

    Parameters
    ----------
    params
        Scene parameter mapping.
    state
        Alignment state to display.
    lens_x
        Lens X position in millimeters.
    axis_z
        Optical-axis height in millimeters.

    Returns
    -------
    tuple[tuple[float, float, float], tuple[float, float, float]]
        Euler rotation and location for the lens and mount.
    """

    exaggeration = float(
        params.get("alignment_display_exaggeration", params["exaggeration"])
    )
    tilt_y_deg = state.tilt_y_deg * exaggeration
    tilt_z_deg = state.tilt_z_deg * exaggeration
    decenter_y_mm = state.decenter_y_mm * exaggeration
    decenter_z_mm = state.decenter_z_mm * exaggeration

    return (
        (0.0, math.radians(-tilt_z_deg), math.radians(tilt_y_deg)),
        (lens_x, decenter_y_mm, axis_z + decenter_z_mm),
    )


def _reflected_summaries_for_state(
    *,
    state: AlignmentState,
    reflected_surfaces: Sequence[LensSurface],
    beam_diameter_mm: float,
    card_to_lens_mm: float,
    sample_rings: int = 4,
) -> tuple[ReflectedSpotSummary, ...]:
    """Trace reflected ray bundles for all displayed surfaces at one state.

    Parameters
    ----------
    state
        Alignment state to trace.
    reflected_surfaces
        Lens surfaces whose back reflections should be displayed.
    beam_diameter_mm
        Incident beam diameter in millimeters.
    card_to_lens_mm
        Distance from the aperture card to the lens center in millimeters.
    sample_rings
        Number of radial rings used to sample each ray bundle.

    Returns
    -------
    tuple[ReflectedSpotSummary, ...]
        Reflected spot summaries in the same order as ``reflected_surfaces``.
    """

    return tuple(
        reflect_ray_bundle_from_surface(
            surface=surface,
            beam_diameter_mm=beam_diameter_mm,
            card_to_lens_mm=card_to_lens_mm,
            tilt_y_deg=state.tilt_y_deg,
            tilt_z_deg=state.tilt_z_deg,
            decenter_y_mm=state.decenter_y_mm,
            decenter_z_mm=state.decenter_z_mm,
            sample_rings=sample_rings,
        )
        for surface in reflected_surfaces
    )


def _display_offset(
    summary: ReflectedSpotSummary, *, exaggeration: float
) -> SpotOffset:
    """Scale a simulated reflected spot center for the visible card readout.

    Parameters
    ----------
    summary
        Reflected spot summary to scale.
    exaggeration
        Visual exaggeration factor.

    Returns
    -------
    SpotOffset
        Spot offset with exaggerated Y/Z coordinates.
    """

    return SpotOffset(
        y_mm=summary.center.y_mm * exaggeration,
        z_mm=summary.center.z_mm * exaggeration,
    )


def _display_radius(summary: ReflectedSpotSummary, *, exaggeration: float) -> float:
    """Scale and clamp a simulated reflected spot diameter for display.

    Parameters
    ----------
    summary
        Reflected spot summary to scale.
    exaggeration
        Visual exaggeration factor.

    Returns
    -------
    float
        Display radius in millimeters.
    """

    return max(0.18, min(1.4, summary.diameter_mm * exaggeration * 0.5))


def _spot_keyframes_for_states(
    *,
    states: Sequence[AlignmentState],
    reflected_surfaces: Sequence[LensSurface],
    beam_diameter_mm: float,
    card_to_lens_mm: float,
    exaggeration: float,
    sample_rings: int = 4,
) -> tuple[tuple[SpotKeyframe, ...], ...]:
    """Compute displayed spot keyframes from ray-traced alignment states.

    Parameters
    ----------
    states
        Ordered alignment states.
    reflected_surfaces
        Lens surfaces whose back reflections should be displayed.
    beam_diameter_mm
        Incident beam diameter in millimeters.
    card_to_lens_mm
        Distance from the aperture card to the lens center in millimeters.
    exaggeration
        Visual exaggeration factor for card offsets and spot radii.
    sample_rings
        Number of radial rings used to sample each ray bundle.

    Returns
    -------
    tuple[tuple[SpotKeyframe, ...], ...]
        One tuple per alignment state, containing one spot keyframe per
        reflected surface.
    """

    return tuple(
        tuple(
            SpotKeyframe(
                frame=state.frame,
                offset=_display_offset(summary, exaggeration=exaggeration),
                radius_mm=_display_radius(summary, exaggeration=exaggeration),
            )
            for summary in _reflected_summaries_for_state(
                state=state,
                reflected_surfaces=reflected_surfaces,
                beam_diameter_mm=beam_diameter_mm,
                card_to_lens_mm=card_to_lens_mm,
                sample_rings=sample_rings,
            )
        )
        for state in states
    )


def main(output_path: str | None = None) -> None:
    """Generate the achromat back-reflection teaching scene.

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
        create_card_closeup_camera,
        create_hero_camera,
        create_wide_camera,
    )
    from simulations.blender.altair_blender.geometry import (
        create_achromat,
        create_business_card,
        create_lens_mount,
        create_optical_table,
        create_scene_label,
        create_studio_backdrop,
    )
    from simulations.blender.altair_blender.materials import create_materials
    from simulations.blender.altair_blender.optics import (
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
    validate_positive("aperture_diameter_mm", params["aperture_diameter_mm"])
    validate_positive("lens_diameter_mm", params["lens_diameter_mm"])

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

    collection = ensure_collection("Achromat Back Reflection")
    materials = create_materials()

    card_x = params["card_x_mm"]
    lens_x = params["lens_x_mm"]
    axis_z = params["optical_axis_z_mm"]
    beam_radius = params["beam_diameter_mm"] / 2.0
    surface_by_name = {surface.name: surface for surface in AC254_100_A.surfaces}
    reflected_surfaces = tuple(
        surface_by_name[name] for name in params["reflected_surfaces"]
    )

    create_optical_table(collection=collection, materials=materials)
    create_studio_backdrop(collection=collection, materials=materials)
    add_area_light(
        name="Large Softbox", location=(35.0, -75.0, 95.0), power=700.0, size=65.0
    )
    add_area_light(
        name="Table Satin Reflection",
        location=(78.0, -8.0, 118.0),
        power=420.0,
        size=130.0,
    )
    add_area_light(
        name="Card Glint Fill", location=(-35.0, -25.0, 55.0), power=160.0, size=20.0
    )
    add_area_light(
        name="Lens Rim Light", location=(116.0, 38.0, 62.0), power=220.0, size=18.0
    )
    create_business_card(
        collection=collection,
        materials=materials,
        x_mm=card_x,
        width_mm=88.0,
        height_mm=50.0,
        aperture_diameter_mm=params["aperture_diameter_mm"],
        optical_axis_z_mm=axis_z,
    )
    lens = create_achromat(
        collection=collection,
        materials=materials,
        x_mm=lens_x,
        diameter_mm=params["lens_diameter_mm"],
        thickness_mm=params["lens_thickness_mm"],
        optical_axis_z_mm=axis_z,
        prescription=AC254_100_A,
    )
    mount = create_lens_mount(
        collection=collection,
        materials=materials,
        x_mm=lens_x,
        diameter_mm=params["lens_diameter_mm"],
        optical_axis_z_mm=axis_z,
        mount=LMR1_MOUNT,
    )

    create_beam_between(
        name="Incident 561 nm Beam",
        start_xyz=(-42.0, 0.0, axis_z),
        end_xyz=(lens_x + 18.0, 0.0, axis_z),
        radius_mm=beam_radius,
        material=materials["laser"],
        collection=collection,
    )

    states = _alignment_states(params)
    spot_keyframes = _spot_keyframes_for_states(
        states=states,
        reflected_surfaces=reflected_surfaces,
        beam_diameter_mm=params["beam_diameter_mm"],
        card_to_lens_mm=lens_x - card_x,
        exaggeration=params["exaggeration"],
        sample_rings=4,
    )

    spot_a = create_return_spot(
        name="Return Spot A",
        card_x_mm=card_x,
        offset=spot_keyframes[0][0].offset,
        radius_mm=spot_keyframes[0][0].radius_mm,
        material=materials["spot_a"],
        collection=collection,
        optical_axis_z_mm=axis_z,
    )
    spot_b = create_return_spot(
        name="Return Spot B",
        card_x_mm=card_x,
        offset=spot_keyframes[0][1].offset,
        radius_mm=spot_keyframes[0][1].radius_mm,
        material=materials["spot_b"],
        collection=collection,
        optical_axis_z_mm=axis_z,
    )

    for obj in (lens, mount):
        for state in states:
            rotation, location = _alignment_display_pose(
                params, state, lens_x=lens_x, axis_z=axis_z
            )
            keyframe_transform(
                obj,
                frame=state.frame,
                rotation_euler=rotation,
                location=location,
            )
        set_linear_interpolation(obj)

    for spot_index, spot in enumerate((spot_a, spot_b)):
        base_radius = spot_keyframes[0][spot_index].radius_mm
        for state_keyframes in spot_keyframes:
            keyframe = state_keyframes[spot_index]
            spot.location = (
                card_x - 0.9,
                keyframe.offset.y_mm,
                axis_z + keyframe.offset.z_mm,
            )
            spot.scale = (
                0.18,
                keyframe.radius_mm / base_radius,
                keyframe.radius_mm / base_radius,
            )
            spot.keyframe_insert(data_path="location", frame=keyframe.frame)
            spot.keyframe_insert(data_path="scale", frame=keyframe.frame)
        set_linear_interpolation(spot)

    if params["show_minimal_labels"]:
        aperture_label, doublet_label, mount_label, reflection_label = params[
            "scene_labels"
        ]
        create_scene_label(
            collection=collection,
            materials=materials,
            name="Label Aperture Card",
            text=aperture_label,
            location=(card_x + 12.0, -42.0, axis_z + 24.0),
            size_mm=2.2,
        )
        create_scene_label(
            collection=collection,
            materials=materials,
            name="Label AC254 Doublet",
            text=doublet_label,
            location=(lens_x - 2.0, -42.0, axis_z + 24.0),
            size_mm=2.2,
        )
        create_scene_label(
            collection=collection,
            materials=materials,
            name="Label LMR1 Mount",
            text=mount_label,
            location=(lens_x + 2.0, -42.0, axis_z - 18.0),
            size_mm=2.0,
        )
        create_scene_label(
            collection=collection,
            materials=materials,
            name="Label Return Reflections",
            text=reflection_label,
            location=(card_x + 8.0, -42.0, axis_z - 17.0),
            size_mm=2.0,
        )

    create_wide_camera(
        target=(70.0, 0.0, axis_z),
        distance_mm=280.0,
        elevation_mm=90.0,
        frame_start=int(params["frame_start"]),
        frame_end=int(params["frame_end"]),
        end_target=(58.0, 0.0, axis_z + 2.0),
        end_distance_mm=230.0,
        end_elevation_mm=78.0,
    )
    create_card_closeup_camera(card_x_mm=card_x, optical_axis_z_mm=axis_z)
    create_hero_camera(
        target=(48.0, 0.0, axis_z + 4.0),
        frame_start=int(params["frame_start"]),
        frame_end=int(params["frame_end"]),
    )

    output = validate_output_path(output_path)
    if output is not None:
        bpy.ops.wm.save_as_mainfile(filepath=str(output))


if __name__ == "__main__":
    main(_parse_output_path(sys.argv))
