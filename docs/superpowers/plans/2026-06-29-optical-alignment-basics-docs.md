# Optical Alignment Basics Documentation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a canonical Basics of Optical Alignment documentation page that embeds the achromat back-reflection movie and gives protocol-like alignment guidance.

**Architecture:** Add one focused RST page under `docs/source/getting_started/`, include it in the first `index.rst` toctree, and replace duplicated baseplate alignment explanation with a cross-link to the canonical page. Add lightweight file-content tests so the docs structure, video embed, fallback link, and cross-link stay in place.

**Tech Stack:** Sphinx/reStructuredText, raw HTML video block, pytest, existing tracked MP4 asset under `docs/source/_static/`.

---

### Task 1: Add Documentation Contract Tests

**Files:**
- Create: `tests/test_optical_alignment_docs.py`

- [ ] **Step 1: Write failing tests for the new docs contract**

Create `tests/test_optical_alignment_docs.py` with tests that assert:

```python
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
INDEX = REPO_ROOT / "docs/source/index.rst"
PAGE = REPO_ROOT / "docs/source/getting_started/optical_alignment_basics.rst"
BASEPLATE_ALIGNMENT = (
    REPO_ROOT / "docs/source/baseplate2_alignment/baseplate2_alignment.rst"
)
VIDEO = (
    REPO_ROOT
    / "docs/source/_static/baseplate2_alignment/alignment/videos/"
    / "achromat_back_reflection_stacked.mp4"
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
    assert "<video controls preload=\"metadata\"" in page
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```bash
uv run --frozen pytest tests/test_optical_alignment_docs.py
```

Expected: fail because `optical_alignment_basics.rst` does not exist and `index.rst` / `baseplate2_alignment.rst` do not yet contain the new links.

### Task 2: Implement The Canonical Alignment Page

**Files:**
- Create: `docs/source/getting_started/optical_alignment_basics.rst`
- Modify: `docs/source/index.rst`
- Modify: `docs/source/baseplate2_alignment/baseplate2_alignment.rst`
- Modify: `docs/superpowers/specs/2026-06-29-optical-alignment-basics-docs-design.md`

- [ ] **Step 1: Amend the spec to require a fallback link**

Add one sentence to the Video Asset section: the raw HTML video embed must be accompanied by a normal RST fallback link to the MP4.

- [ ] **Step 2: Add the new RST page**

Create `docs/source/getting_started/optical_alignment_basics.rst` with:

```rst
.. _optical_alignment_basics:

############################
Basics of Optical Alignment
############################

```

Then add the page content described in the design spec: goal, embedded movie, why the method works, setup, reflection interpretation, step-by-step protocol, and complex optics notes.

- [ ] **Step 3: Add the page to the first toctree**

Insert this entry in `docs/source/index.rst` before `getting_started/getting_started.rst`:

```rst
   getting_started/optical_alignment_basics
```

- [ ] **Step 4: Replace the baseplate-specific duplicate video card with a cross-link**

In `docs/source/baseplate2_alignment/baseplate2_alignment.rst` Step 7, keep the RFO-specific instruction and replace the embedded video card with a short card that links to:

```rst
:ref:`Basics of Optical Alignment <optical_alignment_basics>`
```

### Task 3: Verify And Commit

**Files:**
- Test: `tests/test_optical_alignment_docs.py`
- Test: existing docs files through Sphinx where practical
- Modify: `simulations/blender/scripts/render_achromat_back_reflection_linux.sh`

- [ ] **Step 1: Run the new focused docs tests**

Run:

```bash
uv run --frozen pytest tests/test_optical_alignment_docs.py
```

Expected: pass.

- [ ] **Step 2: Run Blender docs-adjacent tests**

Run:

```bash
uv run --frozen pytest tests/test_optical_alignment_docs.py tests/test_achromat_scene_contract.py tests/test_blender_render_script.py
```

Expected: pass.

- [ ] **Step 3: Fix Linux dry-run portability if verification exposes it**

If `tests/test_blender_render_script.py::test_linux_render_script_dry_run_sets_hpc_defaults`
fails because the local machine does not provide the HPC `module` command, move
the Linux wrapper's module loading behind `--dry-run` detection. Dry-run should
print Linux defaults and delegate to the portable render script without requiring
the HPC environment.

- [ ] **Step 4: Run Sphinx HTML build**

Run:

```bash
uv run --frozen make -C docs html
```

Expected: pass. This verifies the new page renders and the raw HTML block is syntactically acceptable.

- [ ] **Step 5: Run full docs linkcheck if useful**

Run:

```bash
uv run --frozen pytest tests/test_docs.py
```

Expected today may still fail on pre-existing external linkcheck issues in `docs/source/hardware/computer.rst`. If it fails only there, report it separately.

- [ ] **Step 6: Commit the docs implementation**

Run:

```bash
git add docs/source/index.rst docs/source/getting_started/optical_alignment_basics.rst docs/source/baseplate2_alignment/baseplate2_alignment.rst docs/superpowers/specs/2026-06-29-optical-alignment-basics-docs-design.md docs/superpowers/plans/2026-06-29-optical-alignment-basics-docs.md tests/test_optical_alignment_docs.py simulations/blender/scripts/render_achromat_back_reflection_linux.sh
git commit -m "docs: add optical alignment basics guide"
```
