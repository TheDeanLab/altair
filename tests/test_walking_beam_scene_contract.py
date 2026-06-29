from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

import pytest

from simulations.blender.altair_blender.beam_walking import (
    alignment_error_magnitude,
    compute_beam_intercepts,
)

SCENE_PATH = Path("simulations/blender/scenes/walking_beam_alignment.py")
REPO_ROOT = Path(__file__).resolve().parents[1]


def load_scene_module():
    spec = importlib.util.spec_from_file_location("walking_beam_alignment", SCENE_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_scene_script_imports_without_running_blender():
    module = load_scene_module()

    assert module.SCENE_NAME == "walking_beam_alignment"
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

    assert module.SCENE_NAME == "walking_beam_alignment"
    assert str(REPO_ROOT) in sys.path


def test_scene_default_parameters_include_hardware_sources_and_video_contract():
    module = load_scene_module()
    params = module.DEFAULT_PARAMETERS

    assert params["default_render_preset"] == "final"
    assert params["final_video_output_stem"] == "walking_beam_alignment"
    assert params["wide_camera_name"] == "Wide Setup Camera"
    assert params["iris_closeup_camera_name"] == "Iris Close-Up Camera"
    assert params["hero_camera_name"] == "Hero Camera"
    assert params["render_presets"]["final"]["engine"] == "CYCLES"
    assert params["optical_axis_z_mm"] > 0.0

    for source_key in (
        "iris_source",
        "post_holder_source",
        "post_source",
        "mirror_mount_source",
    ):
        assert "Thorlabs" in params[source_key]


def test_scene_uses_requested_one_inch_hole_grid_layout():
    module = load_scene_module()
    params = module.DEFAULT_PARAMETERS

    assert params["hole_grid_spacing_mm"] == pytest.approx(25.4)
    assert params["hole_grid_layout"] == {
        "m1": (-2, -2),
        "m2": (-2, 0),
        "iris_1": (1, 0),
        "iris_2": (3, 0),
    }
    assert module._grid_position_mm(params, "m1") == pytest.approx((-50.8, -50.8))
    assert module._grid_position_mm(params, "m2") == pytest.approx((-50.8, 0.0))
    assert module._grid_position_mm(params, "iris_1") == pytest.approx((25.4, 0.0))
    assert module._grid_position_mm(params, "iris_2") == pytest.approx((76.2, 0.0))

    centers = module._component_centers(params)
    assert centers["m1"][2] == pytest.approx(params["optical_axis_z_mm"])
    assert centers["m2"][2] == pytest.approx(params["optical_axis_z_mm"])
    assert centers["iris_1"][2] == pytest.approx(params["optical_axis_z_mm"])
    assert centers["iris_2"][2] == pytest.approx(params["optical_axis_z_mm"])


def test_scene_defines_explicit_walking_beam_storyboard():
    module = load_scene_module()
    params = module.DEFAULT_PARAMETERS
    states = module._alignment_states(params)

    assert [state.name for state in states] == [
        "gross_misalignment",
        "m1_centers_iris1",
        "m2_centers_iris2",
        "m1_refinement",
        "m2_refinement",
        "aligned_hold",
    ]
    assert [state.frame for state in states] == [
        params["frame_start"],
        params["frame_m1_centers_iris1"],
        params["frame_m2_centers_iris2"],
        params["frame_m1_refinement"],
        params["frame_m2_refinement"],
        params["frame_end"],
    ]


def test_scene_storyboard_reduces_alignment_error_to_zero():
    module = load_scene_module()
    params = module.DEFAULT_PARAMETERS
    model = module._walking_beam_model(params)
    states = module._alignment_states(params)
    errors = [
        alignment_error_magnitude(compute_beam_intercepts(model, state))
        for state in states
    ]

    assert errors[1] < errors[0]
    assert errors[2] < errors[0]
    assert errors[3] < errors[2]
    assert errors[4] < errors[3]
    assert errors[-1] == pytest.approx(0.0, abs=1e-9)
