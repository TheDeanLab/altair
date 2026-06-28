"""Source-backed prescriptions and hardware dimensions for optics scenes."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LensSurface:
    """Spherical optical surface in lens-local millimeter coordinates."""

    name: str
    radius_mm: float
    vertex_x_mm: float
    clear_radius_mm: float
    glass_before: str
    glass_after: str
    reflection_weight: float


@dataclass(frozen=True)
class AchromatPrescription:
    """Cemented achromat dimensions used by visual and ray-tracing helpers."""

    name: str
    diameter_mm: float
    clear_aperture_fraction: float
    effective_focal_length_mm: float
    back_focal_length_mm: float
    first_element_center_thickness_mm: float
    second_element_center_thickness_mm: float
    edge_thickness_mm: float
    surfaces: tuple[LensSurface, ...]
    source_notes: str

    @property
    def clear_aperture_mm(self) -> float:
        return self.diameter_mm * self.clear_aperture_fraction

    @property
    def clear_radius_mm(self) -> float:
        return self.clear_aperture_mm / 2.0

    @property
    def center_thickness_mm(self) -> float:
        return (
            self.first_element_center_thickness_mm
            + self.second_element_center_thickness_mm
        )


@dataclass(frozen=True)
class LensMountPrescription:
    """Simplified dimensions for a fixed lens mount visual model."""

    name: str
    body_width_mm: float
    body_height_mm: float
    body_depth_mm: float
    clear_aperture_mm: float
    optical_axis_height_mm: float
    retaining_ring_depth_mm: float
    source_notes: str


_AC254_DIAMETER_MM = 25.4
_AC254_CLEAR_RADIUS_MM = (_AC254_DIAMETER_MM * 0.90) / 2.0

AC254_100_A = AchromatPrescription(
    name="AC254-100-A",
    diameter_mm=_AC254_DIAMETER_MM,
    clear_aperture_fraction=0.90,
    effective_focal_length_mm=100.1,
    back_focal_length_mm=97.1,
    first_element_center_thickness_mm=4.0,
    second_element_center_thickness_mm=2.5,
    edge_thickness_mm=4.7,
    surfaces=(
        LensSurface(
            name="front_bk7_air",
            radius_mm=62.8,
            vertex_x_mm=-3.25,
            clear_radius_mm=_AC254_CLEAR_RADIUS_MM,
            glass_before="air",
            glass_after="N-BK7",
            reflection_weight=1.0,
        ),
        LensSurface(
            name="cemented_bk7_sf5",
            radius_mm=-45.7,
            vertex_x_mm=0.75,
            clear_radius_mm=_AC254_CLEAR_RADIUS_MM,
            glass_before="N-BK7",
            glass_after="SF5",
            reflection_weight=0.18,
        ),
        LensSurface(
            name="rear_sf5_air",
            radius_mm=-128.2,
            vertex_x_mm=3.25,
            clear_radius_mm=_AC254_CLEAR_RADIUS_MM,
            glass_before="SF5",
            glass_after="air",
            reflection_weight=0.72,
        ),
    ),
    source_notes=(
        "Thorlabs AC254-100-A-ML mounted drawing provides diameter, mounted "
        "center thickness, focal length, working distance, clear aperture, "
        "materials, and coating. AC-series prescription values provide the "
        "three spherical radii and element center thicknesses used for this "
        "geometric teaching model."
    ),
)

LMR1_MOUNT = LensMountPrescription(
    name="LMR1/M",
    body_width_mm=30.5,
    body_height_mm=37.3,
    body_depth_mm=10.2,
    clear_aperture_mm=22.9,
    optical_axis_height_mm=22.1,
    retaining_ring_depth_mm=1.0,
    source_notes=(
        "Thorlabs LMR1/M drawing provides body width, body height, body depth, "
        "clear aperture, optical axis height, retaining-ring depth, and SM1 "
        "thread context for the simplified visual mount."
    ),
)
