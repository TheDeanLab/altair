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
    assert params["mirror_display_exaggeration"] == pytest.approx(1.0)


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


def test_scene_beam_path_uses_nominal_physical_trace_points():
    module = load_scene_module()
    params = module.DEFAULT_PARAMETERS
    centers = module._component_centers(params)
    path = module._beam_path_points(params)
    trace = module._nominal_physical_trace(params)

    assert [point.name for point in path] == [
        "source",
        "m1_surface",
        "m2_surface",
        "iris_row_exit",
    ]
    assert path[0].xyz == pytest.approx(trace.segments[0].start_xyz_mm)
    assert path[1].xyz == pytest.approx(trace.interactions[0].point_xyz_mm)
    assert path[2].xyz == pytest.approx(trace.interactions[1].point_xyz_mm)
    assert path[3].xyz == pytest.approx(trace.segments[-1].end_xyz_mm)
    assert path[1].xyz == pytest.approx(centers["m1"])
    assert path[2].xyz == pytest.approx(centers["m2"])
    assert path[1].xyz[2] == pytest.approx(params["optical_axis_z_mm"])
    assert path[2].xyz[2] == pytest.approx(params["optical_axis_z_mm"])
    assert path[0].xyz[0] < path[1].xyz[0]
    assert path[2].xyz[0] < path[3].xyz[0]


def test_scene_beam_path_hits_finite_mirrors_and_iris_row():
    module = load_scene_module()
    params = module.DEFAULT_PARAMETERS
    centers = module._component_centers(params)
    path = module._beam_path_points(params)
    trace = module._nominal_physical_trace(params)

    assert trace.interactions[0].element_name == "M1"
    assert trace.interactions[1].element_name == "M2"
    assert trace.interactions[0].clearance_margin_mm > 0.0
    assert trace.interactions[1].clearance_margin_mm > 0.0

    assert path[0].xyz[1] == pytest.approx(path[1].xyz[1])
    assert path[1].xyz[0] == pytest.approx(path[2].xyz[0])
    assert path[2].xyz[1] == pytest.approx(centers["iris_1"][1])
    assert path[2].xyz[1] == pytest.approx(path[3].xyz[1])


def test_scene_nominal_physical_trace_hits_all_finite_elements():
    module = load_scene_module()
    params = module.DEFAULT_PARAMETERS

    trace = module._nominal_physical_trace(params)

    assert trace.blocked_at == ""
    assert [interaction.element_name for interaction in trace.interactions] == [
        "M1",
        "M2",
        "Iris 1",
        "Iris 2",
    ]
    assert [interaction.status for interaction in trace.interactions] == [
        "hit",
        "hit",
        "passed",
        "passed",
    ]
    assert all(
        interaction.clearance_margin_mm > 0.0 for interaction in trace.interactions
    )


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

    for state in states:
        trace = module._physical_trace_for_state(params, model, state)
        path = module._downstream_beam_path_for_state(params, model, state)

        assert path.blocked_at == module._blocked_at_key(trace)
        assert path.visible_end_xyz == pytest.approx(trace.segments[-1].end_xyz_mm)
        if len(trace.segments) >= 3:
            assert path.beam_visible is True
            assert path.start_xyz == pytest.approx(trace.segments[2].start_xyz_mm)
        else:
            assert path.beam_visible is False

    aligned = module._downstream_beam_path_for_state(params, model, states[-1])
    assert aligned.iris1_xyz[1:] == pytest.approx(centers["iris_1"][1:])
    assert aligned.iris2_xyz[1:] == pytest.approx(centers["iris_2"][1:])
    assert aligned.start_xyz[0] < aligned.iris1_xyz[0]
    assert aligned.exit_xyz[0] > aligned.iris2_xyz[0]


def test_physical_storyboard_m1_step_centers_near_iris():
    module = load_scene_module()
    params = module.DEFAULT_PARAMETERS
    model = module._walking_beam_model(params)
    states = {state.name: state for state in module._alignment_states(params)}
    gross = module._downstream_beam_path_for_state(
        params,
        model,
        states["gross_misalignment"],
    )
    m1_centered = module._downstream_beam_path_for_state(
        params,
        model,
        states["m1_centers_iris1"],
    )
    centers = module._component_centers(params)

    gross_radius = math.hypot(
        gross.iris1_xyz[1] - centers["iris_1"][1],
        gross.iris1_xyz[2] - centers["iris_1"][2],
    )
    m1_radius = math.hypot(
        m1_centered.iris1_xyz[1] - centers["iris_1"][1],
        m1_centered.iris1_xyz[2] - centers["iris_1"][2],
    )

    assert m1_centered.iris1_visible is True
    assert m1_centered.blocked_at in {"", "iris_2"}
    assert m1_radius < 0.25
    assert m1_radius < gross_radius


def test_physical_storyboard_m2_step_reaches_and_centers_far_iris():
    module = load_scene_module()
    params = module.DEFAULT_PARAMETERS
    model = module._walking_beam_model(params)
    states = {state.name: state for state in module._alignment_states(params)}
    m2_centered = module._downstream_beam_path_for_state(
        params,
        model,
        states["m2_centers_iris2"],
    )
    centers = module._component_centers(params)

    iris1_radius = math.hypot(
        m2_centered.iris1_xyz[1] - centers["iris_1"][1],
        m2_centered.iris1_xyz[2] - centers["iris_1"][2],
    )
    iris2_radius = math.hypot(
        m2_centered.iris2_xyz[1] - centers["iris_2"][1],
        m2_centered.iris2_xyz[2] - centers["iris_2"][2],
    )

    assert m2_centered.iris1_visible is True
    assert m2_centered.iris2_visible is True
    assert m2_centered.blocked_at == ""
    assert iris1_radius < model.iris_radius_mm
    assert iris2_radius < 0.25


def test_mirror_display_rotations_follow_physical_solver_adjustments():
    module = load_scene_module()
    params = module.DEFAULT_PARAMETERS
    model = module._walking_beam_model(params)
    state = module._alignment_states(params)[0]
    m1_adjustment, m2_adjustment = module._mirror_adjustments_for_state(
        params,
        model,
        state,
    )

    m1_rotation = module._mirror_rotation_euler_for_state(params, model, state, "m1")
    m2_rotation = module._mirror_rotation_euler_for_state(params, model, state, "m2")

    assert m1_rotation == pytest.approx(
        (
            m1_adjustment.pitch_mrad / 1000.0,
            0.0,
            math.radians(params["m1_yaw_deg"]) + (m1_adjustment.yaw_mrad / 1000.0),
        )
    )
    assert m2_rotation == pytest.approx(
        (
            m2_adjustment.pitch_mrad / 1000.0,
            0.0,
            math.radians(params["m2_yaw_deg"]) + (m2_adjustment.yaw_mrad / 1000.0),
        )
    )


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
        trace = module._physical_trace_for_state(params, model, state)
        expected_segment = (
            trace.segments[1] if len(trace.segments) >= 2 else trace.segments[0]
        )
        assert folded.start_xyz == pytest.approx(expected_segment.start_xyz_mm)
        assert folded.end_xyz == pytest.approx(expected_segment.end_xyz_mm)
        if downstream.beam_visible:
            assert folded.end_xyz == pytest.approx(downstream.start_xyz)

    assert (
        math.dist(folded_paths["gross_misalignment"].end_xyz, static_path[2].xyz) > 0.1
    )
    assert folded_paths["aligned_hold"].end_xyz == pytest.approx(static_path[2].xyz)


def test_displayed_beam_paths_are_derived_from_physical_trace_segments():
    module = load_scene_module()
    params = module.DEFAULT_PARAMETERS
    model = module._walking_beam_model(params)
    states = module._alignment_states(params)
    aligned = states[-1]

    trace = module._physical_trace_for_state(params, model, aligned)
    folded = module._folded_beam_path_for_state(params, model, aligned)
    downstream = module._downstream_beam_path_for_state(params, model, aligned)

    assert len(trace.segments) >= 5
    assert folded.start_xyz == pytest.approx(trace.segments[1].start_xyz_mm)
    assert folded.end_xyz == pytest.approx(trace.segments[1].end_xyz_mm)
    assert downstream.start_xyz == pytest.approx(trace.segments[2].start_xyz_mm)
    assert downstream.visible_end_xyz == pytest.approx(trace.segments[-1].end_xyz_mm)


def test_hidden_downstream_beam_keeps_nonzero_placeholder_segment():
    module = load_scene_module()
    params = module.DEFAULT_PARAMETERS
    missed_m2_trace = module.trace_two_mirror_two_iris_system(
        source_ray=module._nominal_source_ray(params),
        m1=module.adjusted_plane_mirror(
            module._physical_mirror(params, "m1"),
            adjustment=module.MirrorAdjustment(yaw_mrad=600.0),
        ),
        m2=module._physical_mirror(params, "m2"),
        iris1=module._physical_iris(params, "iris_1"),
        iris2=module._physical_iris(params, "iris_2"),
    )

    path = module._downstream_beam_path_from_trace(params, missed_m2_trace)

    assert path.blocked_at == "m2"
    assert path.beam_visible is False
    assert math.dist(path.start_xyz, path.visible_end_xyz) > 0.0


def test_downstream_beam_path_stops_at_first_blocking_iris():
    module = load_scene_module()
    params = module.DEFAULT_PARAMETERS
    model = module._walking_beam_model(params)
    states = module._alignment_states(params)

    paths = {
        state.name: module._downstream_beam_path_for_state(params, model, state)
        for state in states
    }

    for state in states:
        trace = module._physical_trace_for_state(params, model, state)
        path = paths[state.name]
        assert path.blocked_at == module._blocked_at_key(trace)
        assert path.visible_end_xyz == pytest.approx(trace.segments[-1].end_xyz_mm)

        if path.blocked_at == "iris_1":
            assert path.visible_end_xyz == pytest.approx(path.iris1_xyz)
        elif path.blocked_at == "iris_2":
            assert path.visible_end_xyz == pytest.approx(path.iris2_xyz)
        elif path.blocked_at == "":
            assert path.visible_end_xyz == pytest.approx(path.exit_xyz)


def test_iris_spot_visibility_follows_first_blocking_iris():
    module = load_scene_module()
    params = module.DEFAULT_PARAMETERS
    model = module._walking_beam_model(params)
    states = module._alignment_states(params)

    for state in states:
        trace = module._physical_trace_for_state(params, model, state)
        path = module._downstream_beam_path_for_state(params, model, state)
        reached = {interaction.element_name for interaction in trace.interactions}

        assert module._iris_spot_visibility(path) == (
            "Iris 1" in reached,
            "Iris 2" in reached,
        )


def test_iris_spot_offsets_are_derived_from_physical_trace_points():
    module = load_scene_module()
    params = module.DEFAULT_PARAMETERS
    model = module._walking_beam_model(params)
    states = module._alignment_states(params)
    centers = module._component_centers(params)
    exaggeration = params["spot_display_exaggeration"]

    for state in states:
        path = module._downstream_beam_path_for_state(params, model, state)
        offsets = module._iris_spot_offsets_for_path(params, path)

        assert offsets.iris1.y_mm == pytest.approx(
            (path.iris1_xyz[1] - centers["iris_1"][1]) * exaggeration
        )
        assert offsets.iris1.z_mm == pytest.approx(
            (path.iris1_xyz[2] - centers["iris_1"][2]) * exaggeration
        )
        assert offsets.iris2.y_mm == pytest.approx(
            (path.iris2_xyz[1] - centers["iris_2"][1]) * exaggeration
        )
        assert offsets.iris2.z_mm == pytest.approx(
            (path.iris2_xyz[2] - centers["iris_2"][2]) * exaggeration
        )
