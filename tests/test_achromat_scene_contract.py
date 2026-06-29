import importlib.util
import math
from pathlib import Path
import sys

import pytest  # pyright: ignore[reportMissingImports]

SCENE_PATH = Path("simulations/blender/scenes/achromat_back_reflection.py")
REPO_ROOT = Path(__file__).resolve().parents[1]


def load_scene_module():
    spec = importlib.util.spec_from_file_location(
        "achromat_back_reflection", SCENE_PATH
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_scene_script_imports_without_running_blender():
    module = load_scene_module()

    assert module.SCENE_NAME == "achromat_back_reflection"
    assert callable(module.main)


def test_scene_script_imports_when_executed_by_path_without_repo_on_sys_path(
    monkeypatch,
):
    original_path = list(sys.path)
    filtered_path = [
        path for path in original_path if Path(path or ".").resolve() != REPO_ROOT
    ]
    monkeypatch.setattr(sys, "path", filtered_path)

    module = load_scene_module()

    assert module.SCENE_NAME == "achromat_back_reflection"
    assert str(REPO_ROOT) in sys.path


def test_scene_default_parameters_match_first_demo():
    module = load_scene_module()
    params = module.DEFAULT_PARAMETERS

    assert params["wavelength_nm"] == 561.0
    assert params["beam_diameter_mm"] == 1.0
    assert params["aperture_diameter_mm"] == 1.0
    assert params["lens_focal_length_mm"] == 100.0
    assert params["lens_diameter_mm"] == 25.4
    assert params["lens_thickness_mm"] == 6.5
    assert params["optical_axis_z_mm"] == 22.1
    assert params["reflected_surfaces"] == ("front_bk7_air", "rear_sf5_air")
    assert "Thorlabs AC254-100-A-ML mounted drawing" in params["lens_source"]
    assert "Thorlabs LMR1/M drawing" in params["mount_source"]
    assert params["initial_tilt_y_deg"] != 0.0
    assert params["initial_decenter_y_mm"] != 0.0
    assert params["exaggeration"] > 1.0
    assert params["alignment_display_exaggeration"] > params["exaggeration"]


def test_scene_default_parameters_include_cinematic_video_contract():
    module = load_scene_module()
    params = module.DEFAULT_PARAMETERS

    assert params["show_minimal_labels"] is True
    assert params["hero_camera_name"] == "Hero Camera"
    assert params["default_render_preset"] == "final"
    assert params["render_presets"]["preview"]["engine"] == "BLENDER_EEVEE"
    assert params["render_presets"]["draft"]["engine"] == "BLENDER_WORKBENCH"
    assert params["render_presets"]["final"]["engine"] == "CYCLES"

    labels = params["scene_labels"]
    assert labels == (
        "Aperture card",
        "AC254-100-A doublet",
        "LMR1 mount",
        "Two return reflections",
    )


def test_scene_defines_explicit_alignment_states():
    module = load_scene_module()
    params = module.DEFAULT_PARAMETERS
    states = module._alignment_states(params)

    assert [state.name for state in states] == [
        "rotation_error",
        "angle_corrected",
        "horizontal_decenter",
        "horizontal_corrected",
        "vertical_decenter",
        "aligned",
        "aligned_hold",
    ]
    assert [state.frame for state in states] == [
        params["frame_start"],
        params["frame_tilt_corrected"],
        params["frame_horizontal_decentered"],
        params["frame_horizontal_corrected"],
        params["frame_vertical_decentered"],
        params["frame_vertical_corrected"],
        params["frame_end"],
    ]
    assert states[0].tilt_y_deg == params["initial_tilt_y_deg"]
    assert states[0].decenter_y_mm == 0.0
    assert states[1].tilt_y_deg == 0.0
    assert states[1].decenter_y_mm == 0.0
    assert states[1].decenter_z_mm == 0.0
    assert states[2].tilt_y_deg == 0.0
    assert states[2].decenter_y_mm == params["initial_decenter_y_mm"]
    assert states[2].decenter_z_mm == 0.0
    assert states[3].decenter_y_mm == 0.0
    assert states[3].decenter_z_mm == 0.0
    assert states[4].decenter_y_mm == 0.0
    assert states[4].decenter_z_mm == params["initial_decenter_z_mm"]


def test_scene_keyframes_ray_traced_spot_states():
    module = load_scene_module()
    params = module.DEFAULT_PARAMETERS
    states = module._alignment_states(params)
    reflected_surfaces = tuple(
        surface
        for surface in module.AC254_100_A.surfaces
        if surface.name in params["reflected_surfaces"]
    )

    spot_keyframes = module._spot_keyframes_for_states(
        states=states,
        reflected_surfaces=reflected_surfaces,
        beam_diameter_mm=params["beam_diameter_mm"],
        card_to_lens_mm=params["lens_x_mm"] - params["card_x_mm"],
        exaggeration=params["exaggeration"],
    )

    rotation_offsets = [keyframe.offset for keyframe in spot_keyframes[0]]
    angle_corrected_offsets = [keyframe.offset for keyframe in spot_keyframes[1]]
    horizontal_offsets = [keyframe.offset for keyframe in spot_keyframes[2]]
    horizontal_corrected_offsets = [keyframe.offset for keyframe in spot_keyframes[3]]
    vertical_offsets = [keyframe.offset for keyframe in spot_keyframes[4]]
    aligned_offsets = [keyframe.offset for keyframe in spot_keyframes[5]]

    assert rotation_offsets[0].y_mm < 0.0
    assert rotation_offsets[1].y_mm < 0.0
    assert rotation_offsets[0].z_mm == pytest.approx(0.0, abs=1e-9)
    assert rotation_offsets[1].z_mm == pytest.approx(0.0, abs=1e-9)
    for offset in angle_corrected_offsets:
        assert offset.y_mm == pytest.approx(0.0, abs=1e-9)
        assert offset.z_mm == pytest.approx(0.0, abs=1e-9)
    assert horizontal_offsets[0].y_mm * horizontal_offsets[1].y_mm < 0.0
    assert horizontal_offsets[0].z_mm == pytest.approx(0.0, abs=1e-9)
    assert horizontal_offsets[1].z_mm == pytest.approx(0.0, abs=1e-9)
    for offset in horizontal_corrected_offsets:
        assert offset.y_mm == pytest.approx(0.0, abs=1e-9)
        assert offset.z_mm == pytest.approx(0.0, abs=1e-9)
    assert vertical_offsets[0].z_mm * vertical_offsets[1].z_mm < 0.0
    assert vertical_offsets[0].y_mm == pytest.approx(0.0, abs=1e-9)
    assert vertical_offsets[1].y_mm == pytest.approx(0.0, abs=1e-9)
    for offset in aligned_offsets:
        assert offset.y_mm == pytest.approx(0.0, abs=1e-9)
        assert offset.z_mm == pytest.approx(0.0, abs=1e-9)


def test_scene_exaggerates_displayed_lens_alignment_for_wide_view():
    module = load_scene_module()
    params = module.DEFAULT_PARAMETERS
    lens_x = params["lens_x_mm"]
    axis_z = params["optical_axis_z_mm"]
    exaggeration = params["alignment_display_exaggeration"]
    states = module._alignment_states(params)

    initial_rotation, initial_location = module._alignment_display_pose(
        params,
        states[0],
        lens_x=lens_x,
        axis_z=axis_z,
    )
    tilt_corrected_rotation, tilt_corrected_location = module._alignment_display_pose(
        params,
        states[1],
        lens_x=lens_x,
        axis_z=axis_z,
    )
    final_rotation, final_location = module._alignment_display_pose(
        params,
        states[5],
        lens_x=lens_x,
        axis_z=axis_z,
    )

    assert initial_rotation == (
        0.0,
        0.0,
        math.radians(params["initial_tilt_y_deg"] * exaggeration),
    )
    assert initial_location == (lens_x, 0.0, axis_z)
    assert tilt_corrected_rotation == (0.0, 0.0, 0.0)
    horizontal_decentered_rotation, horizontal_decentered_location = (
        module._alignment_display_pose(
            params,
            states[2],
            lens_x=lens_x,
            axis_z=axis_z,
        )
    )
    assert tilt_corrected_location == (lens_x, 0.0, axis_z)
    assert horizontal_decentered_rotation == (0.0, 0.0, 0.0)
    assert horizontal_decentered_location == (
        lens_x,
        params["initial_decenter_y_mm"] * exaggeration,
        axis_z,
    )
    assert final_rotation == (0.0, 0.0, 0.0)
    assert final_location == (lens_x, 0.0, axis_z)
