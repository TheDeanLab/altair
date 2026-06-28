# Blender Optics Simulations Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a reusable Blender Python simulation area and a first achromatic-doublet back-reflection scene generator for educational optics-alignment videos.

**Architecture:** Add a dedicated `simulations/blender/` area with a small import-safe helper package, `altair_blender`, and one scene script under `scenes/`. Keep quantitative alignment math in pure Python functions that can be tested without Blender, while Blender API calls live behind lazy `bpy` imports so normal repository tests can still run.

**Tech Stack:** Python 3.9+, Blender Python API (`bpy`), standard library `dataclasses` and `math`, pytest, ruff, Sphinx-compatible Markdown documentation.

---

## File Structure

Create or modify these files:

- Create: `simulations/blender/AGENTS.md`
  - Local agent context for the Blender simulation subproject.
- Create: `simulations/blender/README.md`
  - User-facing overview and run instructions.
- Create: `simulations/blender/altair_blender/__init__.py`
  - Package marker and public version string.
- Create: `simulations/blender/altair_blender/optics.py`
  - Pure alignment math plus Blender beam/spot helpers.
- Create: `simulations/blender/altair_blender/scene.py`
  - Lazy Blender import, scene reset, units, render settings, collections.
- Create: `simulations/blender/altair_blender/materials.py`
  - Lazy material creation helpers.
- Create: `simulations/blender/altair_blender/geometry.py`
  - Optical table, business card, aperture, lens, mount, and label geometry.
- Create: `simulations/blender/altair_blender/cameras.py`
  - Wide and card close-up camera creation.
- Create: `simulations/blender/altair_blender/animation.py`
  - Keyframe and interpolation helpers.
- Create: `simulations/blender/scenes/achromat_back_reflection.py`
  - First scene generator and default timeline.
- Create: `tests/test_blender_optics_math.py`
  - Tests for pure return-spot math and validation.
- Create: `tests/test_blender_import_contracts.py`
  - Tests that helper modules import without Blender and expose expected functions.
- Create: `tests/test_achromat_scene_contract.py`
  - Tests that the scene script is import-safe and defines expected parameters.

Do not add generated `.blend`, MP4, GIF, image, or cache files in this implementation.

## Task 1: Scaffold The Blender Simulation Area

**Files:**
- Create: `simulations/blender/AGENTS.md`
- Create: `simulations/blender/README.md`
- Create: `simulations/blender/altair_blender/__init__.py`
- Create directory: `simulations/blender/scenes/`

- [ ] **Step 1: Confirm the working tree before creating files**

Run:

```bash
git status --short
```

Expected: no output, or only changes already known to be part of this plan.

- [ ] **Step 2: Create the simulation directories**

Run:

```bash
mkdir -p simulations/blender/altair_blender simulations/blender/scenes
```

Expected: command exits with status 0.

- [ ] **Step 3: Add local agent context**

Create `simulations/blender/AGENTS.md` with:

````markdown
# Blender Simulation Agent Notes

This directory contains source-controlled Blender Python scene generators for
Altair educational optics-alignment videos.

## Source Of Truth

- Python scene scripts and helper modules are source of truth.
- Generated `.blend`, rendered video, image, cache, and temporary files are build
  artifacts and should not be committed unless a later task explicitly changes
  that policy.

## Coordinate Convention

- Use millimeters as the teaching-scale unit in Python parameters.
- In Blender scene coordinates, 1 Blender unit represents 1 millimeter unless a
  scene-specific script states otherwise.
- The incident laser propagates along positive X by default.
- The business card target is upstream of the lens.
- The card face lies approximately in the Y-Z plane.
- Card aperture and return-spot offsets are expressed as `(y_mm, z_mm)` on the
  card face.

## Modeling Boundary

- These scenes are educational geometric visualizations.
- They should be physically plausible, but they are not quantitative optical
  design solvers.
- Do not claim exact wave optics, exact Fresnel/refraction behavior, or exact
  Zemax equivalence unless a future implementation adds that machinery.
- Visual exaggeration is allowed when an explicit parameter documents it.

## Run Pattern

Run a scene from the repository root with Blender:

```bash
blender --background --python simulations/blender/scenes/achromat_back_reflection.py
```

If Blender is not on `PATH`, document that limitation and run the non-Blender
pytest checks.

## Code Style

- Keep modules import-safe without Blender. Import `bpy` lazily inside functions
  that need it.
- Put reusable helpers in `altair_blender/`.
- Put scene-specific timelines in `scenes/`.
- Prefer explicit names over clever abstractions.
- Keep visual approximation constants visible near the top of scene scripts.
````

- [ ] **Step 4: Add README**

Create `simulations/blender/README.md` with:

````markdown
# Blender Optics Simulations

This directory contains Blender Python source for educational Altair optics
alignment videos.

The scripts build Blender scenes programmatically. The Python source is the
source of truth; generated `.blend` files and rendered movies are build
artifacts.

## First Scene

`scenes/achromat_back_reflection.py` generates a teaching scene for aligning a
mounted achromatic doublet with a narrow collimated 561 nm laser beam. The beam
passes through a small aperture in a business card, reaches the lens, and two
back-reflection spots return to the card. The animation shows tilt correction
followed by decenter correction until both return spots are centered on the
aperture.

The model is intentionally hybrid: it is geometrically plausible and uses
teaching-scale dimensions, but it exaggerates small alignment errors so the
motion is legible in video.

## Run

From the repository root:

```bash
blender --background --python simulations/blender/scenes/achromat_back_reflection.py
```

To save a generated Blender file, pass a path after `--`:

```bash
blender --background --python simulations/blender/scenes/achromat_back_reflection.py -- output/achromat_back_reflection.blend
```

The output directory must already exist.

## Test

Run non-Blender checks from the repository root:

```bash
uv run pytest tests/test_blender_optics_math.py tests/test_blender_import_contracts.py tests/test_achromat_scene_contract.py
```

If `uv run` is not suitable in the local environment, use:

```bash
pytest tests/test_blender_optics_math.py tests/test_blender_import_contracts.py tests/test_achromat_scene_contract.py
```
````

- [ ] **Step 5: Add package marker**

Create `simulations/blender/altair_blender/__init__.py` with:

```python
"""Reusable Blender helpers for Altair educational optics simulations."""

__version__ = "0.1.0"
```

- [ ] **Step 6: Verify formatting-sensitive checks**

Run:

```bash
git diff --check
```

Expected: no output.

- [ ] **Step 7: Commit scaffold**

Run:

```bash
git add simulations/blender/AGENTS.md simulations/blender/README.md simulations/blender/altair_blender/__init__.py
git commit -m "feat: scaffold blender simulation area"
```

Expected: commit succeeds.

## Task 2: Add Pure Alignment Math With Tests

**Files:**
- Create: `simulations/blender/altair_blender/optics.py`
- Create: `tests/test_blender_optics_math.py`

- [ ] **Step 1: Write failing tests for return-spot math**

Create `tests/test_blender_optics_math.py` with:

```python
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


@pytest.mark.parametrize(
    ("name", "value"),
    [
        ("beam_diameter_mm", 0.0),
        ("aperture_diameter_mm", -1.0),
    ],
)
def test_validate_positive_rejects_nonpositive_values(name, value):
    with pytest.raises(ValueError, match=name):
        validate_positive(name, value)


def test_compute_return_spots_rejects_nonpositive_distance_and_exaggeration():
    with pytest.raises(ValueError, match="card_to_lens_mm"):
        compute_return_spots(
            tilt_y_deg=0.0,
            tilt_z_deg=0.0,
            decenter_y_mm=0.0,
            decenter_z_mm=0.0,
            card_to_lens_mm=0.0,
            exaggeration=1.0,
        )

    with pytest.raises(ValueError, match="exaggeration"):
        compute_return_spots(
            tilt_y_deg=0.0,
            tilt_z_deg=0.0,
            decenter_y_mm=0.0,
            decenter_z_mm=0.0,
            card_to_lens_mm=75.0,
            exaggeration=0.0,
        )
```

- [ ] **Step 2: Run tests and verify they fail because the module is missing**

Run:

```bash
uv run pytest tests/test_blender_optics_math.py -q
```

Expected: FAIL with `ModuleNotFoundError` or `ImportError` for `simulations.blender.altair_blender.optics`.

- [ ] **Step 3: Implement pure optics math**

Create `simulations/blender/altair_blender/optics.py` with:

```python
"""Optics helpers for educational Blender alignment scenes.

The numerical helpers in this module are intentionally simple geometric teaching
models. They are not a replacement for optical design software.
"""

from __future__ import annotations

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class SpotOffset:
    """Return-spot offset on the business card face, in millimeters."""

    y_mm: float
    z_mm: float


def validate_positive(name: str, value: float) -> None:
    """Raise a clear error when a physical size or scale is not positive."""

    if value <= 0:
        raise ValueError(f"{name} must be positive; got {value!r}")


def compute_return_spots(
    *,
    tilt_y_deg: float,
    tilt_z_deg: float,
    decenter_y_mm: float,
    decenter_z_mm: float,
    card_to_lens_mm: float,
    exaggeration: float,
    decenter_response: float = 1.0,
) -> tuple[SpotOffset, SpotOffset]:
    """Compute teaching-level return-spot offsets for two lens reflections.

    A lens tilt creates a common walk-off of both reflected spots. A lens
    decenter splits the two surface reflections in opposite directions. The two
    surfaces are given slightly different tilt sensitivity so the viewer can
    distinguish the two return spots during correction.
    """

    validate_positive("card_to_lens_mm", card_to_lens_mm)
    validate_positive("exaggeration", exaggeration)
    validate_positive("decenter_response", decenter_response)

    common_y = 2.0 * math.tan(math.radians(tilt_y_deg)) * card_to_lens_mm * exaggeration
    common_z = 2.0 * math.tan(math.radians(tilt_z_deg)) * card_to_lens_mm * exaggeration
    split_y = decenter_y_mm * decenter_response * exaggeration
    split_z = decenter_z_mm * decenter_response * exaggeration

    spot_a = SpotOffset(
        y_mm=(0.85 * common_y) + split_y,
        z_mm=(0.85 * common_z) + split_z,
    )
    spot_b = SpotOffset(
        y_mm=(1.15 * common_y) - split_y,
        z_mm=(1.15 * common_z) - split_z,
    )
    return spot_a, spot_b
```

- [ ] **Step 4: Run optics tests and verify they pass**

Run:

```bash
uv run pytest tests/test_blender_optics_math.py -q
```

Expected: `6 passed`.

- [ ] **Step 5: Run lint on the new files**

Run:

```bash
uv run ruff check simulations/blender/altair_blender/optics.py tests/test_blender_optics_math.py
```

Expected: `All checks passed!`

If `uv run ruff` is unavailable in the environment, run:

```bash
ruff check simulations/blender/altair_blender/optics.py tests/test_blender_optics_math.py
```

- [ ] **Step 6: Commit optics math**

Run:

```bash
git add simulations/blender/altair_blender/optics.py tests/test_blender_optics_math.py
git commit -m "feat: add blender optics alignment math"
```

Expected: commit succeeds.

## Task 3: Add Import-Safe Scene And Material Helpers

**Files:**
- Create: `simulations/blender/altair_blender/scene.py`
- Create: `simulations/blender/altair_blender/materials.py`
- Create: `tests/test_blender_import_contracts.py`

- [ ] **Step 1: Write failing import-contract tests**

Create `tests/test_blender_import_contracts.py` with:

```python
import importlib

import pytest


def test_scene_and_material_modules_import_without_blender():
    scene = importlib.import_module("simulations.blender.altair_blender.scene")
    materials = importlib.import_module("simulations.blender.altair_blender.materials")

    assert callable(scene.get_bpy)
    assert callable(scene.reset_scene)
    assert callable(scene.configure_scene)
    assert callable(scene.ensure_collection)
    assert callable(materials.create_materials)


def test_get_bpy_reports_clear_error_outside_blender():
    scene = importlib.import_module("simulations.blender.altair_blender.scene")

    with pytest.raises(RuntimeError, match="Blender"):
        scene.get_bpy()
```

- [ ] **Step 2: Run import-contract tests and verify they fail**

Run:

```bash
uv run pytest tests/test_blender_import_contracts.py -q
```

Expected: FAIL because `scene.py` and `materials.py` do not exist.

- [ ] **Step 3: Implement scene helpers**

Create `simulations/blender/altair_blender/scene.py` with:

```python
"""Scene-level helpers for Blender-generated optics simulations."""

from __future__ import annotations

from pathlib import Path
from types import ModuleType


def get_bpy() -> ModuleType:
    """Return Blender's `bpy` module or raise a clear runtime error."""

    try:
        import bpy  # type: ignore[import-not-found]
    except ModuleNotFoundError as exc:
        raise RuntimeError("This function must be run inside Blender with bpy available.") from exc
    return bpy


def reset_scene() -> None:
    """Delete existing objects so the generated scene is deterministic."""

    bpy = get_bpy()
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()


def configure_scene(*, frame_start: int, frame_end: int, fps: int = 24) -> None:
    """Configure units, timeline, render defaults, and world background."""

    bpy = get_bpy()
    scene = bpy.context.scene
    scene.frame_start = frame_start
    scene.frame_end = frame_end
    scene.frame_set(frame_start)
    scene.render.fps = fps
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 0.001
    scene.eevee.taa_render_samples = 64
    scene.world.color = (0.015, 0.018, 0.022)


def ensure_collection(name: str):
    """Return a named collection, creating and linking it when needed."""

    bpy = get_bpy()
    collection = bpy.data.collections.get(name)
    if collection is None:
        collection = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(collection)
    return collection


def validate_output_path(output_path: str | None) -> Path | None:
    """Validate an optional `.blend` output path."""

    if output_path is None:
        return None

    path = Path(output_path).expanduser()
    if not path.parent.exists():
        raise ValueError(f"Output directory does not exist: {path.parent}")
    return path
```

- [ ] **Step 4: Implement material helpers**

Create `simulations/blender/altair_blender/materials.py` with:

```python
"""Reusable material helpers for Blender optics scenes."""

from __future__ import annotations

from .scene import get_bpy


def _material(name: str, color: tuple[float, float, float, float], *, emission: float = 0.0):
    bpy = get_bpy()
    material = bpy.data.materials.new(name)
    material.diffuse_color = color
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get("Principled BSDF")
    if bsdf is not None:
        bsdf.inputs["Base Color"].default_value = color
        bsdf.inputs["Alpha"].default_value = color[3]
        if "Emission Color" in bsdf.inputs:
            bsdf.inputs["Emission Color"].default_value = color
        if "Emission Strength" in bsdf.inputs:
            bsdf.inputs["Emission Strength"].default_value = emission
    material.blend_method = "BLEND"
    return material


def create_materials() -> dict[str, object]:
    """Create the standard material palette for the simulation."""

    return {
        "table": _material("Optical Table Matte Black", (0.025, 0.028, 0.03, 1.0)),
        "metal": _material("Black Anodized Metal", (0.08, 0.085, 0.09, 1.0)),
        "card": _material("Business Card Stock", (0.92, 0.88, 0.78, 1.0)),
        "aperture": _material("Aperture Edge", (0.02, 0.02, 0.018, 1.0)),
        "glass": _material("Coated Achromat Glass", (0.55, 0.82, 0.95, 0.32)),
        "laser": _material("561 nm Laser Beam", (0.35, 1.0, 0.18, 0.65), emission=2.5),
        "spot_a": _material("Return Spot A", (0.45, 1.0, 0.22, 1.0), emission=3.0),
        "spot_b": _material("Return Spot B", (0.18, 0.85, 1.0, 1.0), emission=2.6),
        "label": _material("Subtle Label", (0.9, 0.95, 1.0, 1.0)),
    }
```

- [ ] **Step 5: Run import-contract tests and verify they pass**

Run:

```bash
uv run pytest tests/test_blender_import_contracts.py -q
```

Expected: `2 passed`.

- [ ] **Step 6: Run lint**

Run:

```bash
uv run ruff check simulations/blender/altair_blender/scene.py simulations/blender/altair_blender/materials.py tests/test_blender_import_contracts.py
```

Expected: `All checks passed!`

- [ ] **Step 7: Commit scene and material helpers**

Run:

```bash
git add simulations/blender/altair_blender/scene.py simulations/blender/altair_blender/materials.py tests/test_blender_import_contracts.py
git commit -m "feat: add blender scene and material helpers"
```

Expected: commit succeeds.

## Task 4: Add Geometry And Camera Helpers

**Files:**
- Create: `simulations/blender/altair_blender/geometry.py`
- Create: `simulations/blender/altair_blender/cameras.py`
- Modify: `tests/test_blender_import_contracts.py`

- [ ] **Step 1: Extend import-contract tests for geometry and cameras**

Modify `tests/test_blender_import_contracts.py` to:

```python
import importlib

import pytest


def test_core_modules_import_without_blender():
    scene = importlib.import_module("simulations.blender.altair_blender.scene")
    materials = importlib.import_module("simulations.blender.altair_blender.materials")
    geometry = importlib.import_module("simulations.blender.altair_blender.geometry")
    cameras = importlib.import_module("simulations.blender.altair_blender.cameras")

    assert callable(scene.get_bpy)
    assert callable(scene.reset_scene)
    assert callable(scene.configure_scene)
    assert callable(scene.ensure_collection)
    assert callable(materials.create_materials)
    assert callable(geometry.create_optical_table)
    assert callable(geometry.create_business_card)
    assert callable(geometry.create_achromat)
    assert callable(geometry.create_lens_mount)
    assert callable(cameras.create_wide_camera)
    assert callable(cameras.create_card_closeup_camera)


def test_get_bpy_reports_clear_error_outside_blender():
    scene = importlib.import_module("simulations.blender.altair_blender.scene")

    with pytest.raises(RuntimeError, match="Blender"):
        scene.get_bpy()
```

- [ ] **Step 2: Run tests and verify they fail because modules are missing**

Run:

```bash
uv run pytest tests/test_blender_import_contracts.py -q
```

Expected: FAIL because `geometry.py` and `cameras.py` do not exist.

- [ ] **Step 3: Implement geometry helpers**

Create `simulations/blender/altair_blender/geometry.py` with:

```python
"""Geometry builders for Blender optics alignment scenes."""

from __future__ import annotations

import math

from .scene import get_bpy


def _link_to_collection(obj, collection) -> None:
    for existing in obj.users_collection:
        existing.objects.unlink(obj)
    collection.objects.link(obj)


def create_optical_table(*, collection, materials: dict[str, object], length_mm: float = 220.0, width_mm: float = 90.0):
    bpy = get_bpy()
    bpy.ops.mesh.primitive_cube_add(size=1, location=(70.0, 0.0, -8.0))
    table = bpy.context.object
    table.name = "Optical Table"
    table.dimensions = (length_mm, width_mm, 6.0)
    table.data.materials.append(materials["table"])
    _link_to_collection(table, collection)
    return table


def create_business_card(
    *,
    collection,
    materials: dict[str, object],
    x_mm: float,
    width_mm: float,
    height_mm: float,
    aperture_diameter_mm: float,
):
    bpy = get_bpy()
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x_mm, 0.0, 15.0))
    card = bpy.context.object
    card.name = "Business Card Target"
    card.dimensions = (1.2, width_mm, height_mm)
    card.data.materials.append(materials["card"])
    _link_to_collection(card, collection)

    bpy.ops.mesh.primitive_torus_add(
        major_radius=aperture_diameter_mm * 0.72,
        minor_radius=0.08,
        major_segments=48,
        minor_segments=8,
        location=(x_mm - 0.7, 0.0, 15.0),
        rotation=(0.0, math.radians(90.0), 0.0),
    )
    aperture = bpy.context.object
    aperture.name = "Card Aperture"
    aperture.data.materials.append(materials["aperture"])
    _link_to_collection(aperture, collection)
    return card, aperture


def create_achromat(
    *,
    collection,
    materials: dict[str, object],
    x_mm: float,
    diameter_mm: float,
    thickness_mm: float,
):
    bpy = get_bpy()
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=96,
        radius=diameter_mm / 2.0,
        depth=thickness_mm,
        location=(x_mm, 0.0, 15.0),
        rotation=(0.0, math.radians(90.0), 0.0),
    )
    lens = bpy.context.object
    lens.name = "AC254-100-A-ML Teaching Achromat"
    lens.data.materials.append(materials["glass"])
    _link_to_collection(lens, collection)
    return lens


def create_lens_mount(*, collection, materials: dict[str, object], x_mm: float, diameter_mm: float):
    bpy = get_bpy()
    bpy.ops.mesh.primitive_torus_add(
        major_radius=(diameter_mm / 2.0) + 2.0,
        minor_radius=1.4,
        major_segments=96,
        minor_segments=12,
        location=(x_mm, 0.0, 15.0),
        rotation=(0.0, math.radians(90.0), 0.0),
    )
    mount = bpy.context.object
    mount.name = "Simplified Lens Mount"
    mount.data.materials.append(materials["metal"])
    _link_to_collection(mount, collection)
    return mount
```

- [ ] **Step 4: Implement camera helpers**

Create `simulations/blender/altair_blender/cameras.py` with:

```python
"""Camera helpers for Blender optics alignment scenes."""

from __future__ import annotations

import math

from .scene import get_bpy


def create_wide_camera():
    bpy = get_bpy()
    bpy.ops.object.camera_add(
        location=(35.0, -95.0, 55.0),
        rotation=(math.radians(62.0), 0.0, math.radians(31.0)),
    )
    camera = bpy.context.object
    camera.name = "Wide Setup Camera"
    camera.data.lens = 35
    camera.data.dof.use_dof = True
    camera.data.dof.focus_distance = 95.0
    bpy.context.scene.camera = camera
    return camera


def create_card_closeup_camera(*, card_x_mm: float):
    bpy = get_bpy()
    bpy.ops.object.camera_add(
        location=(card_x_mm - 24.0, -28.0, 20.0),
        rotation=(math.radians(78.0), 0.0, math.radians(-38.0)),
    )
    camera = bpy.context.object
    camera.name = "Card Close-Up Camera"
    camera.data.lens = 80
    camera.data.dof.use_dof = True
    camera.data.dof.focus_distance = 30.0
    return camera
```

- [ ] **Step 5: Run import-contract tests**

Run:

```bash
uv run pytest tests/test_blender_import_contracts.py -q
```

Expected: `2 passed`.

- [ ] **Step 6: Run lint**

Run:

```bash
uv run ruff check simulations/blender/altair_blender/geometry.py simulations/blender/altair_blender/cameras.py tests/test_blender_import_contracts.py
```

Expected: `All checks passed!`

- [ ] **Step 7: Commit geometry and cameras**

Run:

```bash
git add simulations/blender/altair_blender/geometry.py simulations/blender/altair_blender/cameras.py tests/test_blender_import_contracts.py
git commit -m "feat: add blender geometry and camera helpers"
```

Expected: commit succeeds.

## Task 5: Add Animation And Beam Visualization Helpers

**Files:**
- Create: `simulations/blender/altair_blender/animation.py`
- Modify: `simulations/blender/altair_blender/optics.py`
- Modify: `tests/test_blender_import_contracts.py`

- [ ] **Step 1: Extend import-contract tests for animation and beam helpers**

Modify `tests/test_blender_import_contracts.py` to:

```python
import importlib

import pytest


def test_core_modules_import_without_blender():
    scene = importlib.import_module("simulations.blender.altair_blender.scene")
    materials = importlib.import_module("simulations.blender.altair_blender.materials")
    geometry = importlib.import_module("simulations.blender.altair_blender.geometry")
    cameras = importlib.import_module("simulations.blender.altair_blender.cameras")
    animation = importlib.import_module("simulations.blender.altair_blender.animation")
    optics = importlib.import_module("simulations.blender.altair_blender.optics")

    assert callable(scene.get_bpy)
    assert callable(scene.reset_scene)
    assert callable(scene.configure_scene)
    assert callable(scene.ensure_collection)
    assert callable(materials.create_materials)
    assert callable(geometry.create_optical_table)
    assert callable(geometry.create_business_card)
    assert callable(geometry.create_achromat)
    assert callable(geometry.create_lens_mount)
    assert callable(cameras.create_wide_camera)
    assert callable(cameras.create_card_closeup_camera)
    assert callable(animation.keyframe_transform)
    assert callable(animation.set_linear_interpolation)
    assert callable(optics.create_beam_between)
    assert callable(optics.create_return_spot)


def test_get_bpy_reports_clear_error_outside_blender():
    scene = importlib.import_module("simulations.blender.altair_blender.scene")

    with pytest.raises(RuntimeError, match="Blender"):
        scene.get_bpy()
```

- [ ] **Step 2: Run tests and verify they fail**

Run:

```bash
uv run pytest tests/test_blender_import_contracts.py -q
```

Expected: FAIL because `animation.py` does not exist and `optics.create_beam_between` is missing.

- [ ] **Step 3: Implement animation helpers**

Create `simulations/blender/altair_blender/animation.py` with:

```python
"""Animation helpers for Blender optics simulations."""

from __future__ import annotations


def keyframe_transform(obj, *, frame: int, location=None, rotation_euler=None) -> None:
    """Set optional transforms and insert keyframes for them."""

    if location is not None:
        obj.location = location
        obj.keyframe_insert(data_path="location", frame=frame)
    if rotation_euler is not None:
        obj.rotation_euler = rotation_euler
        obj.keyframe_insert(data_path="rotation_euler", frame=frame)


def keyframe_visibility(obj, *, frame: int, visible: bool) -> None:
    """Keyframe viewport and render visibility together."""

    obj.hide_viewport = not visible
    obj.hide_render = not visible
    obj.keyframe_insert(data_path="hide_viewport", frame=frame)
    obj.keyframe_insert(data_path="hide_render", frame=frame)


def set_linear_interpolation(obj) -> None:
    """Set all animation curves for an object to linear interpolation."""

    if obj.animation_data is None or obj.animation_data.action is None:
        return
    for fcurve in obj.animation_data.action.fcurves:
        for keyframe in fcurve.keyframe_points:
            keyframe.interpolation = "LINEAR"
```

- [ ] **Step 4: Add Blender beam and return-spot helpers to optics.py**

Append this code to `simulations/blender/altair_blender/optics.py`:

```python

def create_beam_between(
    *,
    name: str,
    start_xyz: tuple[float, float, float],
    end_xyz: tuple[float, float, float],
    radius_mm: float,
    material,
    collection,
):
    """Create a glowing cylindrical beam between two scene points."""

    from mathutils import Vector  # type: ignore[import-not-found]

    from .scene import get_bpy

    validate_positive("radius_mm", radius_mm)
    bpy = get_bpy()
    start = Vector(start_xyz)
    end = Vector(end_xyz)
    direction = end - start
    length = direction.length
    validate_positive("beam_length", length)

    midpoint = start + (direction * 0.5)
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=radius_mm, depth=length, location=midpoint)
    beam = bpy.context.object
    beam.name = name
    beam.rotation_euler = direction.to_track_quat("Z", "Y").to_euler()
    beam.data.materials.append(material)
    for existing in beam.users_collection:
        existing.objects.unlink(beam)
    collection.objects.link(beam)
    return beam


def create_return_spot(
    *,
    name: str,
    card_x_mm: float,
    offset: SpotOffset,
    radius_mm: float,
    material,
    collection,
):
    """Create a small return spot on the card face."""

    from .scene import get_bpy

    validate_positive("radius_mm", radius_mm)
    bpy = get_bpy()
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=32,
        ring_count=16,
        radius=radius_mm,
        location=(card_x_mm - 0.9, offset.y_mm, 15.0 + offset.z_mm),
    )
    spot = bpy.context.object
    spot.name = name
    spot.scale.x = 0.18
    spot.data.materials.append(material)
    for existing in spot.users_collection:
        existing.objects.unlink(spot)
    collection.objects.link(spot)
    return spot
```

- [ ] **Step 5: Run tests**

Run:

```bash
uv run pytest tests/test_blender_optics_math.py tests/test_blender_import_contracts.py -q
```

Expected: all tests pass.

- [ ] **Step 6: Run lint**

Run:

```bash
uv run ruff check simulations/blender/altair_blender tests/test_blender_optics_math.py tests/test_blender_import_contracts.py
```

Expected: `All checks passed!`

- [ ] **Step 7: Commit animation and beam helpers**

Run:

```bash
git add simulations/blender/altair_blender/animation.py simulations/blender/altair_blender/optics.py tests/test_blender_import_contracts.py
git commit -m "feat: add blender beam and animation helpers"
```

Expected: commit succeeds.

## Task 6: Add The Achromat Back-Reflection Scene Script

**Files:**
- Create: `simulations/blender/scenes/achromat_back_reflection.py`
- Create: `tests/test_achromat_scene_contract.py`

- [ ] **Step 1: Write failing scene contract tests**

Create `tests/test_achromat_scene_contract.py` with:

```python
import importlib.util
from pathlib import Path


SCENE_PATH = Path("simulations/blender/scenes/achromat_back_reflection.py")


def load_scene_module():
    spec = importlib.util.spec_from_file_location("achromat_back_reflection", SCENE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_scene_script_imports_without_running_blender():
    module = load_scene_module()

    assert module.SCENE_NAME == "achromat_back_reflection"
    assert callable(module.main)


def test_scene_default_parameters_match_first_demo():
    module = load_scene_module()
    params = module.DEFAULT_PARAMETERS

    assert params["wavelength_nm"] == 561.0
    assert params["beam_diameter_mm"] == 1.0
    assert params["aperture_diameter_mm"] == 1.0
    assert params["lens_focal_length_mm"] == 100.0
    assert params["lens_diameter_mm"] == 25.4
    assert params["initial_tilt_y_deg"] != 0.0
    assert params["initial_decenter_y_mm"] != 0.0
    assert params["exaggeration"] > 1.0
```

- [ ] **Step 2: Run scene contract tests and verify they fail**

Run:

```bash
uv run pytest tests/test_achromat_scene_contract.py -q
```

Expected: FAIL because `achromat_back_reflection.py` does not exist.

- [ ] **Step 3: Implement scene script**

Create `simulations/blender/scenes/achromat_back_reflection.py` with:

```python
"""Generate the achromat back-reflection alignment teaching scene."""

from __future__ import annotations

import math
from pathlib import Path
import sys


SCENE_NAME = "achromat_back_reflection"

DEFAULT_PARAMETERS = {
    "wavelength_nm": 561.0,
    "beam_diameter_mm": 1.0,
    "aperture_diameter_mm": 1.0,
    "lens_focal_length_mm": 100.0,
    "lens_diameter_mm": 25.4,
    "lens_thickness_mm": 9.0,
    "card_x_mm": 0.0,
    "lens_x_mm": 75.0,
    "initial_tilt_y_deg": 0.28,
    "initial_tilt_z_deg": -0.16,
    "initial_decenter_y_mm": 0.28,
    "initial_decenter_z_mm": -0.18,
    "exaggeration": 8.0,
    "frame_start": 1,
    "frame_tilt_corrected": 72,
    "frame_decenter_corrected": 132,
    "frame_end": 168,
}


def _ensure_repo_root_on_path() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))


def _parse_output_path(argv: list[str]) -> str | None:
    if "--" not in argv:
        return None
    separator = argv.index("--")
    extra = argv[separator + 1 :]
    if not extra:
        return None
    return extra[0]


def main(output_path: str | None = None) -> None:
    _ensure_repo_root_on_path()

    from simulations.blender.altair_blender.animation import keyframe_transform, set_linear_interpolation
    from simulations.blender.altair_blender.cameras import create_card_closeup_camera, create_wide_camera
    from simulations.blender.altair_blender.geometry import (
        create_achromat,
        create_business_card,
        create_lens_mount,
        create_optical_table,
    )
    from simulations.blender.altair_blender.materials import create_materials
    from simulations.blender.altair_blender.optics import (
        compute_return_spots,
        create_beam_between,
        create_return_spot,
        validate_positive,
    )
    from simulations.blender.altair_blender.scene import (
        configure_scene,
        ensure_collection,
        get_bpy,
        reset_scene,
        validate_output_path,
    )

    params = DEFAULT_PARAMETERS
    validate_positive("beam_diameter_mm", params["beam_diameter_mm"])
    validate_positive("aperture_diameter_mm", params["aperture_diameter_mm"])
    validate_positive("lens_diameter_mm", params["lens_diameter_mm"])

    bpy = get_bpy()
    reset_scene()
    configure_scene(
        frame_start=int(params["frame_start"]),
        frame_end=int(params["frame_end"]),
        fps=24,
    )

    collection = ensure_collection("Achromat Back Reflection")
    materials = create_materials()

    card_x = params["card_x_mm"]
    lens_x = params["lens_x_mm"]
    beam_radius = params["beam_diameter_mm"] / 2.0

    create_optical_table(collection=collection, materials=materials)
    create_business_card(
        collection=collection,
        materials=materials,
        x_mm=card_x,
        width_mm=88.0,
        height_mm=50.0,
        aperture_diameter_mm=params["aperture_diameter_mm"],
    )
    lens = create_achromat(
        collection=collection,
        materials=materials,
        x_mm=lens_x,
        diameter_mm=params["lens_diameter_mm"],
        thickness_mm=params["lens_thickness_mm"],
    )
    mount = create_lens_mount(
        collection=collection,
        materials=materials,
        x_mm=lens_x,
        diameter_mm=params["lens_diameter_mm"],
    )

    create_beam_between(
        name="Incident 561 nm Beam",
        start_xyz=(-42.0, 0.0, 15.0),
        end_xyz=(lens_x + 18.0, 0.0, 15.0),
        radius_mm=beam_radius,
        material=materials["laser"],
        collection=collection,
    )

    initial_spots = compute_return_spots(
        tilt_y_deg=params["initial_tilt_y_deg"],
        tilt_z_deg=params["initial_tilt_z_deg"],
        decenter_y_mm=params["initial_decenter_y_mm"],
        decenter_z_mm=params["initial_decenter_z_mm"],
        card_to_lens_mm=lens_x - card_x,
        exaggeration=params["exaggeration"],
    )
    centered_spots = compute_return_spots(
        tilt_y_deg=0.0,
        tilt_z_deg=0.0,
        decenter_y_mm=0.0,
        decenter_z_mm=0.0,
        card_to_lens_mm=lens_x - card_x,
        exaggeration=params["exaggeration"],
    )

    spot_a = create_return_spot(
        name="Return Spot A",
        card_x_mm=card_x,
        offset=initial_spots[0],
        radius_mm=0.65,
        material=materials["spot_a"],
        collection=collection,
    )
    spot_b = create_return_spot(
        name="Return Spot B",
        card_x_mm=card_x,
        offset=initial_spots[1],
        radius_mm=0.55,
        material=materials["spot_b"],
        collection=collection,
    )

    for obj in (lens, mount):
        keyframe_transform(
            obj,
            frame=int(params["frame_start"]),
            rotation_euler=(0.0, math.radians(90.0 + params["initial_tilt_z_deg"]), math.radians(params["initial_tilt_y_deg"])),
            location=(lens_x, params["initial_decenter_y_mm"], 15.0 + params["initial_decenter_z_mm"]),
        )
        keyframe_transform(
            obj,
            frame=int(params["frame_tilt_corrected"]),
            rotation_euler=(0.0, math.radians(90.0), 0.0),
            location=(lens_x, params["initial_decenter_y_mm"], 15.0 + params["initial_decenter_z_mm"]),
        )
        keyframe_transform(
            obj,
            frame=int(params["frame_decenter_corrected"]),
            rotation_euler=(0.0, math.radians(90.0), 0.0),
            location=(lens_x, 0.0, 15.0),
        )
        set_linear_interpolation(obj)

    for spot, final_offset in zip((spot_a, spot_b), centered_spots):
        spot.keyframe_insert(data_path="location", frame=int(params["frame_start"]))
        spot.location = (card_x - 0.9, final_offset.y_mm, 15.0 + final_offset.z_mm)
        spot.keyframe_insert(data_path="location", frame=int(params["frame_decenter_corrected"]))
        set_linear_interpolation(spot)

    create_wide_camera()
    create_card_closeup_camera(card_x_mm=card_x)

    output = validate_output_path(output_path)
    if output is not None:
        bpy.ops.wm.save_as_mainfile(filepath=str(output))


if __name__ == "__main__":
    main(_parse_output_path(sys.argv))
```

- [ ] **Step 4: Run scene contract tests**

Run:

```bash
uv run pytest tests/test_achromat_scene_contract.py -q
```

Expected: `2 passed`.

- [ ] **Step 5: Run all non-Blender tests for the simulation area**

Run:

```bash
uv run pytest tests/test_blender_optics_math.py tests/test_blender_import_contracts.py tests/test_achromat_scene_contract.py -q
```

Expected: all tests pass.

- [ ] **Step 6: Run lint on the simulation area**

Run:

```bash
uv run ruff check simulations/blender tests/test_blender_optics_math.py tests/test_blender_import_contracts.py tests/test_achromat_scene_contract.py
```

Expected: `All checks passed!`

- [ ] **Step 7: Commit scene script**

Run:

```bash
git add simulations/blender/scenes/achromat_back_reflection.py tests/test_achromat_scene_contract.py
git commit -m "feat: add achromat back-reflection blender scene"
```

Expected: commit succeeds.

## Task 7: Verify Blender Smoke Path And Final Documentation

**Files:**
- Modify: `simulations/blender/README.md`
- Modify: `simulations/blender/AGENTS.md` only if verification reveals a durable run note.

- [ ] **Step 1: Check whether Blender is available**

Run:

```bash
command -v blender
```

Expected if Blender is installed: prints the Blender executable path.

Expected if Blender is not installed: exits nonzero with no output. In that case, skip Step 2 and document in the final handoff that Blender smoke verification could not be run locally.

- [ ] **Step 2: Run the scene in Blender when available**

Run:

```bash
blender --background --python simulations/blender/scenes/achromat_back_reflection.py
```

Expected: Blender exits with status 0 and does not report Python exceptions.

- [ ] **Step 3: Save a temporary `.blend` file outside source control when Blender is available**

Run:

```bash
mkdir -p /tmp/altair-blender-smoke
blender --background --python simulations/blender/scenes/achromat_back_reflection.py -- /tmp/altair-blender-smoke/achromat_back_reflection.blend
test -f /tmp/altair-blender-smoke/achromat_back_reflection.blend
```

Expected: all commands exit with status 0. Do not commit the generated file.

- [ ] **Step 4: Update README with verification note if needed**

If Blender was unavailable, append this section to `simulations/blender/README.md`:

````markdown
## Local Verification Notes

The non-Blender tests exercise import safety, parameter validation, and the
teaching-level return-spot math. Full scene generation requires Blender on
`PATH` and should be smoke-tested with:

```bash
blender --background --python simulations/blender/scenes/achromat_back_reflection.py
```
````

If Blender was available and the smoke test passed, no README change is required.

- [ ] **Step 5: Run final non-Blender verification**

Run:

```bash
uv run pytest tests/test_blender_optics_math.py tests/test_blender_import_contracts.py tests/test_achromat_scene_contract.py -q
uv run ruff check simulations/blender tests/test_blender_optics_math.py tests/test_blender_import_contracts.py tests/test_achromat_scene_contract.py
git diff --check
```

Expected: pytest passes, ruff reports `All checks passed!`, and `git diff --check` has no output.

- [ ] **Step 6: Inspect source-control status**

Run:

```bash
git status --short
```

Expected:

- If Blender was unavailable and README was updated, only `simulations/blender/README.md` is modified.
- If Blender was available and no docs update was required, no output.

- [ ] **Step 7: Commit final verification docs only if README or AGENTS changed**

Run this only when Step 6 shows documentation changes:

```bash
git add simulations/blender/README.md simulations/blender/AGENTS.md
git commit -m "docs: update blender simulation verification notes"
```

Expected: commit succeeds when there are documentation changes. If there are no changes, do not create an empty commit.

## Final Handoff Checklist

Before reporting completion:

- [ ] Run `git log --oneline -5` and include the new commits in the handoff.
- [ ] Run `git status --short` and confirm whether the tree is clean.
- [ ] Report exact verification commands run and whether Blender smoke verification was run or skipped.
- [ ] Do not claim rendered video or generated `.blend` artifacts were committed.
- [ ] Mention that the first script is the source of truth for the scene.

## Plan Self-Review

Spec coverage:

- Dedicated `simulations/blender/` area: Task 1.
- Reusable helper modules: Tasks 2 through 5.
- Local `AGENTS.md`: Task 1.
- First achromat back-reflection scene: Task 6.
- Hybrid educational model and explicit approximation boundary: Tasks 1, 2, 6.
- Parameterized values for 561 nm beam, 1 mm beam/aperture, 100 mm focal length, lens diameter, tilt, decenter, and exaggeration: Task 6.
- Wide and close-up cameras: Tasks 4 and 6.
- Tests without Blender plus optional Blender smoke: Tasks 2, 3, 4, 5, 6, and 7.
- Documentation and generated-artifact policy: Tasks 1 and 7.

Placeholder scan: no unfinished-work markers or unspecified edge-handling steps remain.

Type consistency: `SpotOffset`, `compute_return_spots`, `validate_positive`, `get_bpy`, `create_materials`, geometry helpers, camera helpers, animation helpers, and scene constants are defined before later tasks rely on them.
