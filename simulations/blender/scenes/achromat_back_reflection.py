"""Generate the achromat back-reflection alignment teaching scene."""

from __future__ import annotations

import math
from pathlib import Path
import sys


SCENE_NAME = "achromat_back_reflection"

DEFAULT_PARAMETERS = {
    "wavelength_nm": 561.0,
    "beam_diameter_mm": 1.0,
    "aperture_diameter_mm": 1.0,
    "lens_focal_length_mm": 100.0,
    "lens_diameter_mm": 25.4,
    "lens_thickness_mm": 9.0,
    "card_x_mm": 0.0,
    "lens_x_mm": 75.0,
    "initial_tilt_y_deg": 0.28,
    "initial_tilt_z_deg": -0.16,
    "initial_decenter_y_mm": 0.28,
    "initial_decenter_z_mm": -0.18,
    "exaggeration": 8.0,
    "frame_start": 1,
    "frame_tilt_corrected": 72,
    "frame_decenter_corrected": 132,
    "frame_end": 168,
}


def _ensure_repo_root_on_path() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))


def _parse_output_path(argv: list[str]) -> str | None:
    if "--" not in argv:
        return None
    separator = argv.index("--")
    extra = argv[separator + 1 :]
    if not extra:
        return None
    return extra[0]


def main(output_path: str | None = None) -> None:
    _ensure_repo_root_on_path()

    from simulations.blender.altair_blender.animation import (
        keyframe_transform,
        set_linear_interpolation,
    )
    from simulations.blender.altair_blender.cameras import (
        create_card_closeup_camera,
        create_wide_camera,
    )
    from simulations.blender.altair_blender.geometry import (
        create_achromat,
        create_business_card,
        create_lens_mount,
        create_optical_table,
    )
    from simulations.blender.altair_blender.materials import create_materials
    from simulations.blender.altair_blender.optics import (
        compute_return_spots,
        create_beam_between,
        create_return_spot,
        validate_positive,
    )
    from simulations.blender.altair_blender.scene import (
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
    )

    collection = ensure_collection("Achromat Back Reflection")
    materials = create_materials()

    card_x = params["card_x_mm"]
    lens_x = params["lens_x_mm"]
    beam_radius = params["beam_diameter_mm"] / 2.0

    create_optical_table(collection=collection, materials=materials)
    create_business_card(
        collection=collection,
        materials=materials,
        x_mm=card_x,
        width_mm=88.0,
        height_mm=50.0,
        aperture_diameter_mm=params["aperture_diameter_mm"],
    )
    lens = create_achromat(
        collection=collection,
        materials=materials,
        x_mm=lens_x,
        diameter_mm=params["lens_diameter_mm"],
        thickness_mm=params["lens_thickness_mm"],
    )
    mount = create_lens_mount(
        collection=collection,
        materials=materials,
        x_mm=lens_x,
        diameter_mm=params["lens_diameter_mm"],
    )

    create_beam_between(
        name="Incident 561 nm Beam",
        start_xyz=(-42.0, 0.0, 15.0),
        end_xyz=(lens_x + 18.0, 0.0, 15.0),
        radius_mm=beam_radius,
        material=materials["laser"],
        collection=collection,
    )

    initial_spots = compute_return_spots(
        tilt_y_deg=params["initial_tilt_y_deg"],
        tilt_z_deg=params["initial_tilt_z_deg"],
        decenter_y_mm=params["initial_decenter_y_mm"],
        decenter_z_mm=params["initial_decenter_z_mm"],
        card_to_lens_mm=lens_x - card_x,
        exaggeration=params["exaggeration"],
    )
    centered_spots = compute_return_spots(
        tilt_y_deg=0.0,
        tilt_z_deg=0.0,
        decenter_y_mm=0.0,
        decenter_z_mm=0.0,
        card_to_lens_mm=lens_x - card_x,
        exaggeration=params["exaggeration"],
    )

    spot_a = create_return_spot(
        name="Return Spot A",
        card_x_mm=card_x,
        offset=initial_spots[0],
        radius_mm=0.65,
        material=materials["spot_a"],
        collection=collection,
    )
    spot_b = create_return_spot(
        name="Return Spot B",
        card_x_mm=card_x,
        offset=initial_spots[1],
        radius_mm=0.55,
        material=materials["spot_b"],
        collection=collection,
    )

    for obj in (lens, mount):
        keyframe_transform(
            obj,
            frame=int(params["frame_start"]),
            rotation_euler=(
                0.0,
                math.radians(90.0 + params["initial_tilt_z_deg"]),
                math.radians(params["initial_tilt_y_deg"]),
            ),
            location=(
                lens_x,
                params["initial_decenter_y_mm"],
                15.0 + params["initial_decenter_z_mm"],
            ),
        )
        keyframe_transform(
            obj,
            frame=int(params["frame_tilt_corrected"]),
            rotation_euler=(0.0, math.radians(90.0), 0.0),
            location=(
                lens_x,
                params["initial_decenter_y_mm"],
                15.0 + params["initial_decenter_z_mm"],
            ),
        )
        keyframe_transform(
            obj,
            frame=int(params["frame_decenter_corrected"]),
            rotation_euler=(0.0, math.radians(90.0), 0.0),
            location=(lens_x, 0.0, 15.0),
        )
        set_linear_interpolation(obj)

    for spot, final_offset in zip((spot_a, spot_b), centered_spots):
        spot.keyframe_insert(data_path="location", frame=int(params["frame_start"]))
        spot.location = (card_x - 0.9, final_offset.y_mm, 15.0 + final_offset.z_mm)
        spot.keyframe_insert(
            data_path="location", frame=int(params["frame_decenter_corrected"])
        )
        set_linear_interpolation(spot)

    create_wide_camera()
    create_card_closeup_camera(card_x_mm=card_x)

    output = validate_output_path(output_path)
    if output is not None:
        bpy.ops.wm.save_as_mainfile(filepath=str(output))


if __name__ == "__main__":
    main(_parse_output_path(sys.argv))
