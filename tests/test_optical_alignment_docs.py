from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
INDEX = REPO_ROOT / "docs/source/index.rst"
PAGE = REPO_ROOT / "docs/source/getting_started/optical_alignment_basics.rst"
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


def test_optical_alignment_basics_is_in_first_toc():
    index = INDEX.read_text()

    assert "getting_started/optical_alignment_basics" in index
    assert index.index("getting_started/optical_alignment_basics") < index.index(
        "getting_started/getting_started.rst"
    )


def test_optical_alignment_basics_embeds_video_with_fallback():
    assert VIDEO.exists()
    page = PAGE.read_text()

    assert ".. _optical_alignment_basics:" in page
    assert "Basics of Optical Alignment" in page
    assert '<video controls preload="metadata"' in page
    assert VIDEO_SOURCE in page
    assert "`Download the alignment movie" in page
    assert "goal is to make the optic normal to the incoming beam" in page


def test_optical_alignment_basics_contains_protocol_and_interpretation():
    page = PAGE.read_text()

    for expected in (
        "Why This Works",
        "Step-By-Step Protocol",
        "Interpreting The Reflection Spots",
        "Complex Optics",
        "Spherical or curved surfaces",
        "The aperture card is part of the measurement",
    ):
        assert expected in page


def test_baseplate_alignment_links_to_canonical_alignment_page():
    page = BASEPLATE_ALIGNMENT.read_text()

    assert ":ref:`Basics of Optical Alignment <optical_alignment_basics>`" in page
