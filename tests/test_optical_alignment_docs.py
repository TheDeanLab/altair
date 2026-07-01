from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
INDEX = REPO_ROOT / "docs/source/index.rst"
LANDING = REPO_ROOT / "docs/source/getting_started/optical_alignment_basics.rst"
BACK_REFLECTIONS = REPO_ROOT / (
    "docs/source/getting_started/optical_alignment_back_reflections.rst"
)
WALKING_BEAM = REPO_ROOT / (
    "docs/source/getting_started/optical_alignment_walking_beam.rst"
)
BASEPLATE_ALIGNMENT = REPO_ROOT / (
    "docs/source/baseplate2_alignment/baseplate2_alignment.rst"
)
VIDEO = REPO_ROOT / (
    "docs/source/_static/baseplate2_alignment/alignment/videos/"
    "achromat_back_reflection_stacked.mp4"
)
VIDEO_SOURCE = (
    "../_static/baseplate2_alignment/alignment/videos/"
    "achromat_back_reflection_stacked.mp4"
)
WALKING_VIDEO = REPO_ROOT / (
    "docs/source/_static/optical_alignment/videos/" "walking_beam_alignment_stacked.mp4"
)
WALKING_VIDEO_SOURCE = (
    "../_static/optical_alignment/videos/walking_beam_alignment_stacked.mp4"
)


def test_optical_alignment_basics_is_in_first_toc():
    index = INDEX.read_text()

    assert "getting_started/optical_alignment_basics" in index
    assert index.index("getting_started/optical_alignment_basics") < index.index(
        "getting_started/getting_started.rst"
    )


def test_optical_alignment_basics_is_landing_page_for_alignment_tutorials():
    page = LANDING.read_text()

    assert ".. _optical_alignment_basics:" in page
    assert "Basics of Optical Alignment" in page
    assert ".. toctree::" in page
    assert "optical_alignment_back_reflections" in page
    assert "optical_alignment_walking_beam" in page
    assert "in development" in page
    assert "GitHub feature requests" in page
    for expected in (
        "Finding the focus of a beam",
        "Collimating a beam",
        "Walking a beam",
        "Setting up an alignment laser",
    ):
        assert expected in page


def test_back_reflection_alignment_embeds_video_with_fallback():
    assert VIDEO.exists()
    page = BACK_REFLECTIONS.read_text()

    assert ".. _optical_alignment_back_reflections:" in page
    assert "Back-Reflection Alignment" in page
    assert '<video controls preload="metadata"' in page
    assert VIDEO_SOURCE in page
    assert "`Download the alignment movie" in page
    assert "goal is to make the optic normal to the incoming beam" in page


def test_back_reflection_alignment_contains_protocol_and_interpretation():
    page = BACK_REFLECTIONS.read_text()

    for expected in (
        "Why This Works",
        "Step-By-Step Protocol",
        "Interpreting The Reflection Spots",
        "Complex Optics",
        "Spherical or curved surfaces",
        "The aperture card is part of the measurement",
    ):
        assert expected in page


def test_walking_beam_alignment_embeds_video_with_fallback():
    assert WALKING_VIDEO.exists()
    page = WALKING_BEAM.read_text()

    assert ".. _optical_alignment_walking_beam:" in page
    assert "Walking A Beam Through Two Irises" in page
    assert '<video controls preload="metadata"' in page
    assert WALKING_VIDEO_SOURCE in page
    assert "`Download the walking-beam alignment movie" in page


def test_walking_beam_alignment_contains_required_tutorial_sections():
    page = WALKING_BEAM.read_text()

    for expected in (
        "Goal",
        "Why This Works",
        "Step-By-Step Protocol",
        "Troubleshooting",
        "Adjust the first mirror to center the near iris",
        "Adjust the second mirror to center the far iris",
    ):
        assert expected in page


def test_baseplate_alignment_links_to_canonical_alignment_page():
    page = BASEPLATE_ALIGNMENT.read_text()

    assert (
        ":ref:`Back-Reflection Alignment <optical_alignment_back_reflections>`" in page
    )
