from __future__ import annotations

import pytest

from simulations.blender.altair_blender.prescriptions import (
    AC254_100_A,
    ID25_IRIS,
    KM100CP_MOUNT,
    LMR1_MOUNT,
    PH2_POST_HOLDER,
    TR15_POST,
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


def test_id25_iris_dimensions_match_source_values() -> None:
    assert ID25_IRIS.name == "ID25"
    assert ID25_IRIS.min_aperture_mm == pytest.approx(1.4)
    assert ID25_IRIS.max_aperture_mm == pytest.approx(25.0)
    assert ID25_IRIS.outer_diameter_mm == pytest.approx(43.7)
    assert ID25_IRIS.thickness_mm == pytest.approx(6.6)
    assert ID25_IRIS.leaf_count == 14
    assert "Thorlabs post-mountable iris diaphragm table" in ID25_IRIS.source_notes


def test_ph2_post_holder_and_tr15_post_dimensions_match_source_values() -> None:
    assert PH2_POST_HOLDER.name == "PH2"
    assert PH2_POST_HOLDER.accepted_post_diameter_mm == pytest.approx(12.7)
    assert PH2_POST_HOLDER.length_mm == pytest.approx(50.8)
    assert "Thorlabs PH2 product page" in PH2_POST_HOLDER.source_notes

    assert TR15_POST.name == "TR1.5"
    assert TR15_POST.diameter_mm == pytest.approx(12.7)
    assert TR15_POST.length_mm == pytest.approx(38.1)
    assert TR15_POST.top_thread == "8-32"
    assert TR15_POST.bottom_thread == "1/4-20"
    assert "Thorlabs TR1.5 product page" in TR15_POST.source_notes


def test_km100cp_mount_dimensions_match_source_values() -> None:
    assert KM100CP_MOUNT.name == "KM100CP"
    assert KM100CP_MOUNT.optic_diameter_mm == pytest.approx(25.4)
    assert KM100CP_MOUNT.clear_aperture_mm == pytest.approx(23.9)
    assert KM100CP_MOUNT.body_width_mm == pytest.approx(49.9)
    assert KM100CP_MOUNT.body_height_mm == pytest.approx(49.9)
    assert KM100CP_MOUNT.angular_range_deg == pytest.approx(4.0)
    assert KM100CP_MOUNT.adjuster_mrad_per_revolution == pytest.approx(8.0)
    assert "Thorlabs KM100CP product page" in KM100CP_MOUNT.source_notes
