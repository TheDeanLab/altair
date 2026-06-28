from __future__ import annotations

import pytest

from simulations.blender.altair_blender.prescriptions import (
    AC254_100_A,
    LMR1_MOUNT,
)


def test_ac254_100_a_prescription_matches_source_values() -> None:
    assert AC254_100_A.name == "AC254-100-A"
    assert AC254_100_A.diameter_mm == pytest.approx(25.4)
    assert AC254_100_A.clear_aperture_mm == pytest.approx(22.86)
    assert AC254_100_A.effective_focal_length_mm == pytest.approx(100.1)
    assert AC254_100_A.back_focal_length_mm == pytest.approx(97.1)
    assert AC254_100_A.center_thickness_mm == pytest.approx(6.5)
    assert AC254_100_A.edge_thickness_mm == pytest.approx(4.7)

    surfaces = AC254_100_A.surfaces
    assert [surface.name for surface in surfaces] == [
        "front_bk7_air",
        "cemented_bk7_sf5",
        "rear_sf5_air",
    ]
    assert [surface.radius_mm for surface in surfaces] == pytest.approx(
        [62.8, -45.7, -128.2]
    )
    assert [surface.vertex_x_mm for surface in surfaces] == pytest.approx(
        [-3.25, 0.75, 3.25]
    )


def test_ac254_surface_sources_are_explicit() -> None:
    assert "Thorlabs AC254-100-A-ML mounted drawing" in AC254_100_A.source_notes
    assert "AC-series prescription" in AC254_100_A.source_notes
    assert AC254_100_A.surfaces[0].glass_before == "air"
    assert AC254_100_A.surfaces[0].glass_after == "N-BK7"
    assert AC254_100_A.surfaces[1].glass_before == "N-BK7"
    assert AC254_100_A.surfaces[1].glass_after == "SF5"
    assert AC254_100_A.surfaces[2].glass_before == "SF5"
    assert AC254_100_A.surfaces[2].glass_after == "air"


def test_lmr1_mount_dimensions_match_drawing_values() -> None:
    assert LMR1_MOUNT.name == "LMR1/M"
    assert LMR1_MOUNT.body_width_mm == pytest.approx(30.5)
    assert LMR1_MOUNT.body_height_mm == pytest.approx(37.3)
    assert LMR1_MOUNT.body_depth_mm == pytest.approx(10.2)
    assert LMR1_MOUNT.clear_aperture_mm == pytest.approx(22.9)
    assert LMR1_MOUNT.optical_axis_height_mm == pytest.approx(22.1)
    assert "Thorlabs LMR1/M drawing" in LMR1_MOUNT.source_notes
