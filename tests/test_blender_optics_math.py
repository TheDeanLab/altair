import math

import pytest

from simulations.blender.altair_blender.optics import (
    SpotOffset,
    compute_return_spots,
    validate_positive,
)


def test_compute_return_spots_zero_alignment_centers_both_spots():
    spot_a, spot_b = compute_return_spots(
        tilt_y_deg=0.0,
        tilt_z_deg=0.0,
        decenter_y_mm=0.0,
        decenter_z_mm=0.0,
        card_to_lens_mm=75.0,
        exaggeration=10.0,
    )

    assert spot_a == SpotOffset(y_mm=0.0, z_mm=0.0)
    assert spot_b == SpotOffset(y_mm=0.0, z_mm=0.0)


def test_compute_return_spots_tilt_creates_common_offset():
    spot_a, spot_b = compute_return_spots(
        tilt_y_deg=0.25,
        tilt_z_deg=-0.10,
        decenter_y_mm=0.0,
        decenter_z_mm=0.0,
        card_to_lens_mm=75.0,
        exaggeration=8.0,
    )

    assert spot_a.y_mm > 0
    assert spot_b.y_mm > spot_a.y_mm
    assert spot_a.z_mm < 0
    assert spot_b.z_mm < spot_a.z_mm


def test_compute_return_spots_decenter_splits_spots_oppositely():
    spot_a, spot_b = compute_return_spots(
        tilt_y_deg=0.0,
        tilt_z_deg=0.0,
        decenter_y_mm=0.20,
        decenter_z_mm=-0.10,
        card_to_lens_mm=75.0,
        exaggeration=6.0,
    )

    assert math.isclose(spot_a.y_mm, -spot_b.y_mm)
    assert math.isclose(spot_a.z_mm, -spot_b.z_mm)
    assert spot_a.y_mm > 0
    assert spot_b.y_mm < 0
    assert spot_a.z_mm < 0
    assert spot_b.z_mm > 0


def test_compute_return_spots_mixed_alignment_matches_expected_offsets():
    spot_a, spot_b = compute_return_spots(
        tilt_y_deg=0.5,
        tilt_z_deg=-0.25,
        decenter_y_mm=0.10,
        decenter_z_mm=-0.05,
        card_to_lens_mm=100.0,
        exaggeration=4.0,
        decenter_response=0.5,
    )

    assert spot_a.y_mm == pytest.approx(6.1342700977159765)
    assert spot_a.z_mm == pytest.approx(-3.0670785580770654)
    assert spot_b.y_mm == pytest.approx(7.828718367498085)
    assert spot_b.z_mm == pytest.approx(-3.914282755045441)


@pytest.mark.parametrize(
    ("name", "value"),
    [
        ("beam_diameter_mm", 0.0),
        ("aperture_diameter_mm", -1.0),
        ("working_distance_mm", math.nan),
        ("focal_length_mm", math.inf),
        ("spacing_mm", -math.inf),
    ],
)
def test_validate_positive_rejects_nonpositive_and_nonfinite_values(name, value):
    with pytest.raises(ValueError, match=name):
        validate_positive(name, value)


@pytest.mark.parametrize(
    ("name", "kwargs"),
    [
        ("card_to_lens_mm", {"card_to_lens_mm": 0.0}),
        ("exaggeration", {"exaggeration": 0.0}),
        ("decenter_response", {"decenter_response": 0.0}),
        ("decenter_response", {"decenter_response": math.nan}),
        ("decenter_response", {"decenter_response": math.inf}),
    ],
)
def test_compute_return_spots_rejects_invalid_positive_parameters(name, kwargs):
    parameters = {
        "tilt_y_deg": 0.0,
        "tilt_z_deg": 0.0,
        "decenter_y_mm": 0.0,
        "decenter_z_mm": 0.0,
        "card_to_lens_mm": 75.0,
        "exaggeration": 1.0,
    }
    parameters.update(kwargs)

    with pytest.raises(ValueError, match=name):
        compute_return_spots(
            **parameters,
        )
