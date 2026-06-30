from __future__ import annotations

import math

import pytest

from simulations.blender.altair_blender.beam_walking import (
    CircularAperture,
    MirrorAdjustment,
    PlaneMirror,
    Ray3D,
    adjusted_plane_mirror,
    trace_two_mirror_two_iris_system,
    trace_circular_aperture,
    trace_plane_mirror,
)


def test_finite_plane_mirror_reports_hit_and_reflected_ray() -> None:
    mirror = PlaneMirror(
        name="M1",
        center_xyz_mm=(0.0, 0.0, 0.0),
        normal_xyz=(0.0, -1.0, 0.0),
        clear_radius_mm=12.0,
    )
    ray = Ray3D(
        origin_xyz_mm=(0.0, -25.0, 0.0),
        direction_xyz=(0.0, 1.0, 0.0),
        beam_radius_mm=0.5,
    )

    interaction, reflected = trace_plane_mirror(ray=ray, mirror=mirror)

    assert interaction.status == "hit"
    assert interaction.element_name == "M1"
    assert interaction.point_xyz_mm == pytest.approx((0.0, 0.0, 0.0))
    assert interaction.local_y_mm == pytest.approx(0.0)
    assert interaction.local_z_mm == pytest.approx(0.0)
    assert interaction.clearance_margin_mm == pytest.approx(11.5)
    assert reflected is not None
    assert reflected.origin_xyz_mm == pytest.approx((0.0, 0.0, 0.0))
    assert reflected.direction_xyz == pytest.approx((0.0, -1.0, 0.0))


def test_finite_plane_mirror_reports_missed_clear_aperture() -> None:
    mirror = PlaneMirror(
        name="M1",
        center_xyz_mm=(0.0, 0.0, 0.0),
        normal_xyz=(0.0, -1.0, 0.0),
        clear_radius_mm=12.0,
    )
    ray = Ray3D(
        origin_xyz_mm=(13.0, -25.0, 0.0),
        direction_xyz=(0.0, 1.0, 0.0),
        beam_radius_mm=0.5,
    )

    interaction, reflected = trace_plane_mirror(ray=ray, mirror=mirror)

    assert interaction.status == "missed_clear_aperture"
    assert interaction.radial_offset_mm == pytest.approx(13.0)
    assert interaction.clearance_margin_mm == pytest.approx(-1.5)
    assert reflected is None


def test_mirror_yaw_adjustment_changes_reflected_angle_by_twice_the_tilt() -> None:
    mirror = PlaneMirror(
        name="M1",
        center_xyz_mm=(0.0, 0.0, 0.0),
        normal_xyz=(0.0, -1.0, 0.0),
        clear_radius_mm=12.0,
    )
    adjusted = adjusted_plane_mirror(
        mirror,
        adjustment=MirrorAdjustment(yaw_mrad=5.0, pitch_mrad=0.0),
    )
    ray = Ray3D(
        origin_xyz_mm=(0.0, -25.0, 0.0),
        direction_xyz=(0.0, 1.0, 0.0),
        beam_radius_mm=0.5,
    )

    interaction, reflected = trace_plane_mirror(ray=ray, mirror=adjusted)

    assert interaction.status == "hit"
    assert reflected is not None
    reflected_angle_mrad = (
        math.atan2(
            reflected.direction_xyz[0],
            -reflected.direction_xyz[1],
        )
        * 1000.0
    )
    assert reflected_angle_mrad == pytest.approx(10.0, abs=0.001)


def test_circular_aperture_distinguishes_pass_clip_and_block() -> None:
    aperture = CircularAperture(
        name="Iris 1",
        center_xyz_mm=(10.0, 0.0, 0.0),
        normal_xyz=(-1.0, 0.0, 0.0),
        aperture_radius_mm=1.25,
        body_radius_mm=20.0,
    )

    centered = Ray3D(
        origin_xyz_mm=(0.0, 0.0, 0.0),
        direction_xyz=(1.0, 0.0, 0.0),
        beam_radius_mm=0.5,
    )
    clipped = Ray3D(
        origin_xyz_mm=(0.0, 0.9, 0.0),
        direction_xyz=(1.0, 0.0, 0.0),
        beam_radius_mm=0.5,
    )
    blocked = Ray3D(
        origin_xyz_mm=(0.0, 3.0, 0.0),
        direction_xyz=(1.0, 0.0, 0.0),
        beam_radius_mm=0.5,
    )

    centered_interaction, centered_ray = trace_circular_aperture(
        ray=centered,
        aperture=aperture,
    )
    clipped_interaction, clipped_ray = trace_circular_aperture(
        ray=clipped,
        aperture=aperture,
    )
    blocked_interaction, blocked_ray = trace_circular_aperture(
        ray=blocked,
        aperture=aperture,
    )

    assert centered_interaction.status == "passed"
    assert centered_interaction.clearance_margin_mm == pytest.approx(0.75)
    assert centered_ray is not None
    assert clipped_interaction.status == "clipped"
    assert clipped_interaction.clearance_margin_mm == pytest.approx(-0.15)
    assert clipped_ray is not None
    assert blocked_interaction.status == "blocked"
    assert blocked_interaction.clearance_margin_mm == pytest.approx(-2.25)
    assert blocked_ray is None


def test_two_mirror_two_iris_trace_records_successful_chain() -> None:
    diagonal_normal = (-(2**-0.5), 2**-0.5, 0.0)
    source = Ray3D(
        origin_xyz_mm=(-20.0, 0.0, 0.0),
        direction_xyz=(1.0, 0.0, 0.0),
        beam_radius_mm=0.5,
    )
    m1 = PlaneMirror(
        name="M1",
        center_xyz_mm=(0.0, 0.0, 0.0),
        normal_xyz=diagonal_normal,
        clear_radius_mm=12.0,
    )
    m2 = PlaneMirror(
        name="M2",
        center_xyz_mm=(0.0, 20.0, 0.0),
        normal_xyz=diagonal_normal,
        clear_radius_mm=12.0,
    )
    iris1 = CircularAperture(
        name="Iris 1",
        center_xyz_mm=(25.0, 20.0, 0.0),
        normal_xyz=(-1.0, 0.0, 0.0),
        aperture_radius_mm=1.25,
        body_radius_mm=20.0,
    )
    iris2 = CircularAperture(
        name="Iris 2",
        center_xyz_mm=(50.0, 20.0, 0.0),
        normal_xyz=(-1.0, 0.0, 0.0),
        aperture_radius_mm=1.25,
        body_radius_mm=20.0,
    )

    trace = trace_two_mirror_two_iris_system(
        source_ray=source,
        m1=m1,
        m2=m2,
        iris1=iris1,
        iris2=iris2,
    )

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
    assert len(trace.segments) == 5
    assert trace.segments[-1].start_xyz_mm == pytest.approx((50.0, 20.0, 0.0))
    assert trace.segments[-1].end_xyz_mm[0] > 50.0


def test_two_mirror_two_iris_trace_stops_at_missed_second_mirror() -> None:
    diagonal_normal = (-(2**-0.5), 2**-0.5, 0.0)
    source = Ray3D(
        origin_xyz_mm=(-20.0, 0.0, 0.0),
        direction_xyz=(1.0, 0.0, 0.0),
        beam_radius_mm=0.5,
    )
    m1 = PlaneMirror(
        name="M1",
        center_xyz_mm=(0.0, 0.0, 0.0),
        normal_xyz=diagonal_normal,
        clear_radius_mm=12.0,
    )
    m2 = PlaneMirror(
        name="M2",
        center_xyz_mm=(0.0, 20.0, 13.0),
        normal_xyz=diagonal_normal,
        clear_radius_mm=12.0,
    )
    iris1 = CircularAperture(
        name="Iris 1",
        center_xyz_mm=(25.0, 20.0, 0.0),
        normal_xyz=(-1.0, 0.0, 0.0),
        aperture_radius_mm=1.25,
        body_radius_mm=20.0,
    )
    iris2 = CircularAperture(
        name="Iris 2",
        center_xyz_mm=(50.0, 20.0, 0.0),
        normal_xyz=(-1.0, 0.0, 0.0),
        aperture_radius_mm=1.25,
        body_radius_mm=20.0,
    )

    trace = trace_two_mirror_two_iris_system(
        source_ray=source,
        m1=m1,
        m2=m2,
        iris1=iris1,
        iris2=iris2,
    )

    assert trace.blocked_at == "M2"
    assert [interaction.element_name for interaction in trace.interactions] == [
        "M1",
        "M2",
    ]
    assert trace.interactions[-1].status == "missed_clear_aperture"
    assert len(trace.segments) == 2
    assert trace.segments[-1].end_xyz_mm == pytest.approx(
        trace.interactions[-1].point_xyz_mm
    )
