from __future__ import annotations

import pytest

from simulations.blender.altair_blender.beam_walking import (
    CircularAperture,
    PlaneMirror,
    Ray3D,
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
