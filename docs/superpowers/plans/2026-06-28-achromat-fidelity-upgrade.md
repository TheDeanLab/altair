# Achromat Fidelity Upgrade Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade the Blender achromat alignment scene with AC254-style doublet geometry, reflected ray-bundle spots, LMR1-style mount geometry, and shadows.

**Architecture:** Add import-safe optical prescription and ray tracing helpers, then have Blender geometry functions consume those helpers. The scene remains the orchestration layer: it owns parameters and animation timing while reusable modules own physical calculations and mesh construction.

**Tech Stack:** Python 3, pytest, Blender Python API, ffmpeg render script.

---

## File Structure

- Create `simulations/blender/altair_blender/prescriptions.py` for source-backed lens and mount data classes.
- Modify `simulations/blender/altair_blender/optics.py` to add spherical surfaces and ray-bundle reflection summaries while preserving existing helpers where useful.
- Modify `simulations/blender/altair_blender/geometry.py` to create an AC254-style doublet mesh and an LMR1-style mount.
- Modify `simulations/blender/altair_blender/materials.py` for separate BK7, SF5, coating, reflection, and mount materials.
- Modify `simulations/blender/altair_blender/scene.py` to enable lighting and shadows.
- Modify `simulations/blender/scenes/achromat_back_reflection.py` to use prescription-derived geometry and ray-bundle spot summaries.
- Update `simulations/blender/README.md` and `simulations/blender/AGENTS.md` with the fidelity model boundary.
- Add tests in `tests/test_blender_prescriptions.py` and expand `tests/test_blender_optics_math.py` and `tests/test_achromat_scene_contract.py`.

## Tasks

### Task 1: Prescription Data

- [ ] Write failing tests asserting AC254 prescription constants, clear aperture, source labels, and LMR1 dimensions.
- [ ] Add `prescriptions.py` with frozen data classes and constants.
- [ ] Run the new prescription tests and confirm they pass.

### Task 2: Ray-Bundle Reflection Math

- [ ] Write failing tests for spherical sag, surface normals, centered aligned reflections, tilt/decenter offsets, and unequal spot diameters.
- [ ] Implement vector math, spherical-surface intersection, reflection, card-plane intersection, and bundle footprint summarization in `optics.py`.
- [ ] Run optics tests and confirm old and new helpers pass together.

### Task 3: Blender Geometry

- [ ] Write failing import/contract tests for new object names expected in the scene.
- [ ] Replace the cylinder achromat with two mesh elements using prescription surfaces.
- [ ] Replace the torus mount with an LMR1-style mount body, bore, retaining ring, spanner slots, base, and post features.
- [ ] Add material keys for BK7, SF5, coating, reflection beams, and mount surfaces.

### Task 4: Scene Integration

- [ ] Update scene defaults to AC254 prescription values and source labels.
- [ ] Use ray-bundle spot summaries for animated return spot centers and radii.
- [ ] Add optional faint reflected beam cylinders from lens surfaces back toward the card.
- [ ] Enable shadows and area lights in the scene setup.

### Task 5: Docs And Verification

- [ ] Update README and AGENTS notes to describe the prescription/ray model and its teaching boundary.
- [ ] Run focused pytest, ruff check, and ruff format check.
- [ ] Run Blender background scene generation.
- [ ] Run a two-frame render-script smoke test and confirm `.blend`, PNG sequences, and three MP4s are produced.
- [ ] Commit and push the branch update.
