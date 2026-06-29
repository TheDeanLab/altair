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
        """Return the usable optical aperture diameter.

        Returns
        -------
        float
            Clear aperture diameter in millimeters.
        """

        return self.diameter_mm * self.clear_aperture_fraction

    @property
    def clear_radius_mm(self) -> float:
        """Return the usable optical aperture radius.

        Returns
        -------
        float
            Clear aperture radius in millimeters.
        """

        return self.clear_aperture_mm / 2.0

    @property
    def center_thickness_mm(self) -> float:
        """Return total center thickness of the cemented doublet.

        Returns
        -------
        float
            Combined element center thickness in millimeters.
        """

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


@dataclass(frozen=True)
class IrisPrescription:
    """Simplified source-backed dimensions for a post-mounted iris."""

    name: str
    min_aperture_mm: float
    max_aperture_mm: float
    outer_diameter_mm: float
    thickness_mm: float
    leaf_count: int
    source_notes: str


@dataclass(frozen=True)
class PostHolderPrescription:
    """Simplified source-backed dimensions for a post holder."""

    name: str
    accepted_post_diameter_mm: float
    length_mm: float
    source_notes: str


@dataclass(frozen=True)
class OpticalPostPrescription:
    """Simplified source-backed dimensions for an optical post."""

    name: str
    diameter_mm: float
    length_mm: float
    top_thread: str
    bottom_thread: str
    source_notes: str


@dataclass(frozen=True)
class MirrorMountPrescription:
    """Simplified source-backed dimensions for a kinematic mirror mount."""

    name: str
    optic_diameter_mm: float
    clear_aperture_mm: float
    body_width_mm: float
    body_height_mm: float
    body_depth_mm: float
    angular_range_deg: float
    adjuster_mrad_per_revolution: float
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

ID25_IRIS = IrisPrescription(
    name="ID25",
    min_aperture_mm=1.4,
    max_aperture_mm=25.0,
    outer_diameter_mm=43.7,
    thickness_mm=6.6,
    leaf_count=14,
    source_notes=(
        "Thorlabs post-mountable iris diaphragm table lists ID25 with "
        "1.4 mm to 25.0 mm aperture range, 14 leaves, and 1.72 in / "
        "0.26 in (43.7 mm / 6.6 mm) outer diameter and thickness."
    ),
)

PH2_POST_HOLDER = PostHolderPrescription(
    name="PH2",
    accepted_post_diameter_mm=12.7,
    length_mm=50.8,
    source_notes=(
        "Thorlabs PH2 product page lists a spring-loaded hex-locking "
        "thumbscrew post holder for 1/2 in (12.7 mm) posts with L = 2 in "
        "(50.8 mm)."
    ),
)

TR15_POST = OpticalPostPrescription(
    name="TR1.5",
    diameter_mm=12.7,
    length_mm=38.1,
    top_thread="8-32",
    bottom_thread="1/4-20",
    source_notes=(
        "Thorlabs TR1.5 product page lists a 1/2 in (12.7 mm) stainless "
        "optical post with L = 1.5 in (38.1 mm), an 8-32 setscrew, and a "
        "1/4-20 tap."
    ),
)

KM100CP_MOUNT = MirrorMountPrescription(
    name="KM100CP",
    optic_diameter_mm=25.4,
    clear_aperture_mm=23.9,
    body_width_mm=49.9,
    body_height_mm=49.9,
    body_depth_mm=10.2,
    angular_range_deg=4.0,
    adjuster_mrad_per_revolution=8.0,
    source_notes=(
        "Thorlabs KM100CP product page identifies the post-centered "
        "kinematic mirror mount for 1 in (25.4 mm) optics with two 1/4-80 "
        "adjusters, +/-4 deg angular range, and 8 mrad per revolution "
        "adjustment. The KM100-family drawing gives a 0.94 in (23.9 mm) "
        "clear aperture and 1.97 in (49.9 mm) front-plate width and height "
        "for the simplified visual model."
    ),
)
