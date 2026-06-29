from __future__ import annotations

import importlib.util
import math
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


def test_scene_uses_narrow_visible_iris_apertures_with_reticles():
    module = load_scene_module()
    params = module.DEFAULT_PARAMETERS

    assert params["iris_display_aperture_mm"] == pytest.approx(
        params["alignment_aperture_diameter_mm"]
    )
    assert params["iris_reticle_radius_mm"] > params["iris_display_aperture_mm"] / 2.0
    assert params["iris_reticle_faces"] == "both"


def test_scene_uses_consistent_display_exaggeration_for_beam_and_spots():
    module = load_scene_module()
    params = module.DEFAULT_PARAMETERS

    assert params["beam_path_offset_exaggeration"] == pytest.approx(
        params["spot_display_exaggeration"]
    )
    assert params["beam_path_offset_exaggeration"] > 1.0


def test_scene_separates_physical_beam_size_from_rendered_readability():
    module = load_scene_module()
    params = module.DEFAULT_PARAMETERS

    assert params["beam_diameter_mm"] == pytest.approx(1.0)
    assert params["beam_visual_diameter_mm"] > params["beam_diameter_mm"]
    assert module._beam_visual_radius(params) == pytest.approx(
        params["beam_visual_diameter_mm"] / 2.0
    )
    assert module._iris_spot_radius(params) > 0.85


def test_scene_uses_requested_one_inch_hole_grid_layout():
    module = load_scene_module()
    params = module.DEFAULT_PARAMETERS

    assert params["hole_grid_spacing_mm"] == pytest.approx(25.4)
    assert params["hole_grid_layout"] == {
        "m1": (-2, -2),
        "m2": (-2, 0),
        "iris_1": (1, 0),
        "iris_2": (6, 0),
    }
    assert module._grid_position_mm(params, "m1") == pytest.approx((-50.8, -50.8))
    assert module._grid_position_mm(params, "m2") == pytest.approx((-50.8, 0.0))
    assert module._grid_position_mm(params, "iris_1") == pytest.approx((25.4, 0.0))
    assert module._grid_position_mm(params, "iris_2") == pytest.approx((152.4, 0.0))

    centers = module._component_centers(params)
    assert centers["m1"][2] == pytest.approx(params["optical_axis_z_mm"])
    assert centers["m2"][2] == pytest.approx(params["optical_axis_z_mm"])
    assert centers["iris_1"][2] == pytest.approx(params["optical_axis_z_mm"])
    assert centers["iris_2"][2] == pytest.approx(params["optical_axis_z_mm"])
    assert centers["iris_2"][0] - centers["iris_1"][0] == pytest.approx(127.0)


def test_scene_orients_mirror_mount_faces_toward_the_beam_path():
    module = load_scene_module()
    params = module.DEFAULT_PARAMETERS

    assert params["m1_yaw_deg"] == pytest.approx(-45.0)
    assert params["m2_yaw_deg"] == pytest.approx(135.0)

    m1_reflective_normal = (
        -math.cos(math.radians(params["m1_yaw_deg"])),
        -math.sin(math.radians(params["m1_yaw_deg"])),
    )
    assert m1_reflective_normal[0] < 0.0
    assert m1_reflective_normal[1] > 0.0


def test_scene_mirror_yaws_trace_ninety_degree_reflections():
    module = load_scene_module()
    params = module.DEFAULT_PARAMETERS

    incoming = (1.0, 0.0, 0.0)
    m1_normal = module._mirror_reflective_normal(params["m1_yaw_deg"])
    folded = module._reflect_direction(incoming, m1_normal)
    m2_normal = module._mirror_reflective_normal(params["m2_yaw_deg"])
    outgoing = module._reflect_direction(folded, m2_normal)

    assert folded[0] == pytest.approx(0.0, abs=1e-9)
    assert folded[1] > 0.0
    assert outgoing[0] > 0.0
    assert outgoing[1] == pytest.approx(0.0, abs=1e-9)


def test_scene_static_z_fold_path_is_ray_traced_from_mirror_planes():
    module = load_scene_module()
    params = module.DEFAULT_PARAMETERS

    trace = module._trace_z_fold_ray(params)
    assert trace == module._beam_path_points(params)

    source, m1_hit, m2_hit, exit_point = (point.xyz for point in trace)

    def unit_vector(start, end):
        delta = tuple(end[index] - start[index] for index in range(3))
        length = math.sqrt(sum(component * component for component in delta))
        return tuple(component / length for component in delta)

    incoming = unit_vector(source, m1_hit)
    folded = unit_vector(m1_hit, m2_hit)
    outgoing = unit_vector(m2_hit, exit_point)

    assert module._reflect_direction(
        incoming, module._mirror_reflective_normal(params["m1_yaw_deg"])
    ) == pytest.approx(folded, abs=1e-9)
    assert module._reflect_direction(
        folded, module._mirror_reflective_normal(params["m2_yaw_deg"])
    ) == pytest.approx(outgoing, abs=1e-9)


def test_scene_beam_path_uses_mirror_surface_points_not_mount_centers():
    module = load_scene_module()
    params = module.DEFAULT_PARAMETERS
    centers = module._component_centers(params)
    path = module._beam_path_points(params)

    assert [point.name for point in path] == [
        "source",
        "m1_surface",
        "m2_surface",
        "iris_row_exit",
    ]
    assert path[1].xyz != centers["m1"]
    assert path[2].xyz != centers["m2"]
    assert path[1].xyz[2] == pytest.approx(params["optical_axis_z_mm"])
    assert path[2].xyz[2] == pytest.approx(params["optical_axis_z_mm"])
    assert path[0].xyz[0] < path[1].xyz[0]
    assert path[2].xyz[0] < path[3].xyz[0]


def test_scene_beam_path_hits_visible_mirror_face_planes_and_iris_row():
    module = load_scene_module()
    params = module.DEFAULT_PARAMETERS
    centers = module._component_centers(params)
    path = module._beam_path_points(params)

    for component_name, yaw_key, point in (
        ("m1", "m1_yaw_deg", path[1]),
        ("m2", "m2_yaw_deg", path[2]),
    ):
        yaw_rad = math.radians(params[yaw_key])
        normal_xy = (math.cos(yaw_rad), math.sin(yaw_rad))
        center = centers[component_name]
        face_offset = (point.xyz[0] - center[0]) * normal_xy[0] + (
            point.xyz[1] - center[1]
        ) * normal_xy[1]

        assert face_offset == pytest.approx(-params["mirror_surface_offset_mm"])

    assert path[0].xyz[1] == pytest.approx(path[1].xyz[1])
    assert path[1].xyz[0] == pytest.approx(path[2].xyz[0])
    assert path[2].xyz[1] == pytest.approx(centers["iris_1"][1])
    assert path[2].xyz[1] == pytest.approx(path[3].xyz[1])


def test_iris_closeup_camera_pose_frames_both_irises():
    module = load_scene_module()
    params = module.DEFAULT_PARAMETERS
    centers = module._component_centers(params)
    pose = module._iris_closeup_camera_pose(params)
    iris_midpoint_x = (centers["iris_1"][0] + centers["iris_2"][0]) / 2.0

    assert pose.target_xyz[0] == pytest.approx(iris_midpoint_x)
    assert pose.location_xyz[0] == pytest.approx(iris_midpoint_x)
    assert pose.location_xyz[1] < -180.0
    assert pose.location_xyz[2] > params["optical_axis_z_mm"]
    assert pose.lens_mm <= 40.0


def test_wide_camera_plan_keeps_final_still_on_full_layout():
    module = load_scene_module()
    params = module.DEFAULT_PARAMETERS
    centers = module._component_centers(params)
    plan = module._wide_camera_plan(params)
    span_midpoint_x = (centers["m1"][0] + centers["iris_2"][0]) / 2.0

    assert plan.target_xyz[0] == pytest.approx(span_midpoint_x)
    assert plan.end_target_xyz[0] == pytest.approx(span_midpoint_x)
    assert plan.distance_mm >= 330.0
    assert plan.end_distance_mm >= 320.0
    assert plan.end_elevation_mm >= 118.0


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


def test_scene_storyboard_captions_cover_alignment_sequence():
    module = load_scene_module()
    params = module.DEFAULT_PARAMETERS
    states = module._alignment_states(params)
    captions = module._storyboard_captions_for_states(params, states)

    assert [caption.frame for caption in captions] == [state.frame for state in states]
    assert [caption.state_name for caption in captions] == [
        state.name for state in states
    ]
    assert captions[0].text == "Start: beam misses both irises"
    assert "M1 adjust" in captions[1].text
    assert "M2 adjust" in captions[2].text
    assert captions[-1].text == "Aligned: both irises centered"
    assert params["storyboard_caption_location_mm"][2] > params["optical_axis_z_mm"]


def test_scene_uses_high_contrast_label_style_for_caption_readability():
    module = load_scene_module()
    params = module.DEFAULT_PARAMETERS
    style = module._label_style(params)

    assert style.color == pytest.approx((1.0, 0.96, 0.7, 1.0))
    assert style.emission_strength >= 1.4


def test_downstream_beam_path_tracks_iterative_alignment_states():
    module = load_scene_module()
    params = module.DEFAULT_PARAMETERS
    model = module._walking_beam_model(params)
    states = module._alignment_states(params)
    centers = module._component_centers(params)

    paths = {
        state.name: module._downstream_beam_path_for_state(params, model, state)
        for state in states
    }

    gross = paths["gross_misalignment"]
    assert gross.iris1_xyz[1:] != pytest.approx(centers["iris_1"][1:])
    assert gross.iris2_xyz[1:] != pytest.approx(centers["iris_2"][1:])

    m1_centered = paths["m1_centers_iris1"]
    assert m1_centered.iris1_xyz[1:] == pytest.approx(centers["iris_1"][1:])
    assert m1_centered.iris2_xyz[1:] != pytest.approx(centers["iris_2"][1:])

    m2_centered = paths["m2_centers_iris2"]
    assert m2_centered.iris1_xyz[1:] != pytest.approx(centers["iris_1"][1:])
    assert m2_centered.iris2_xyz[1:] == pytest.approx(centers["iris_2"][1:])

    aligned = paths["aligned_hold"]
    assert aligned.iris1_xyz[1:] == pytest.approx(centers["iris_1"][1:])
    assert aligned.iris2_xyz[1:] == pytest.approx(centers["iris_2"][1:])
    assert aligned.start_xyz[0] < aligned.iris1_xyz[0]
    assert aligned.exit_xyz[0] > aligned.iris2_xyz[0]


def test_folded_beam_path_shares_animated_m2_hit_point():
    module = load_scene_module()
    params = module.DEFAULT_PARAMETERS
    model = module._walking_beam_model(params)
    states = module._alignment_states(params)
    static_path = module._beam_path_points(params)

    folded_paths = {
        state.name: module._folded_beam_path_for_state(params, model, state)
        for state in states
    }
    downstream_paths = {
        state.name: module._downstream_beam_path_for_state(params, model, state)
        for state in states
    }

    for state in states:
        folded = folded_paths[state.name]
        downstream = downstream_paths[state.name]
        assert folded.start_xyz == pytest.approx(static_path[1].xyz)
        assert folded.end_xyz == pytest.approx(downstream.start_xyz)

    assert (
        math.dist(folded_paths["gross_misalignment"].end_xyz, static_path[2].xyz) > 0.1
    )
    assert folded_paths["aligned_hold"].end_xyz == pytest.approx(static_path[2].xyz)


def test_downstream_beam_path_stops_at_first_blocking_iris():
    module = load_scene_module()
    params = module.DEFAULT_PARAMETERS
    model = module._walking_beam_model(params)
    states = module._alignment_states(params)

    paths = {
        state.name: module._downstream_beam_path_for_state(params, model, state)
        for state in states
    }

    assert paths["gross_misalignment"].blocked_at == "iris_1"
    assert paths["gross_misalignment"].visible_end_xyz == pytest.approx(
        paths["gross_misalignment"].iris1_xyz
    )

    assert paths["m1_centers_iris1"].blocked_at == "iris_2"
    assert paths["m1_centers_iris1"].visible_end_xyz == pytest.approx(
        paths["m1_centers_iris1"].iris2_xyz
    )

    assert paths["m2_centers_iris2"].blocked_at == "iris_1"
    assert paths["m2_centers_iris2"].visible_end_xyz == pytest.approx(
        paths["m2_centers_iris2"].iris1_xyz
    )

    assert paths["aligned_hold"].blocked_at == ""
    assert paths["aligned_hold"].visible_end_xyz == pytest.approx(
        paths["aligned_hold"].exit_xyz
    )


def test_iris_spot_visibility_follows_first_blocking_iris():
    module = load_scene_module()
    params = module.DEFAULT_PARAMETERS
    model = module._walking_beam_model(params)
    states = module._alignment_states(params)

    visibility = {
        state.name: module._iris_spot_visibility(
            module._downstream_beam_path_for_state(params, model, state)
        )
        for state in states
    }

    assert visibility["gross_misalignment"] == (True, False)
    assert visibility["m1_centers_iris1"] == (True, True)
    assert visibility["m2_centers_iris2"] == (True, False)
    assert visibility["aligned_hold"] == (True, True)
