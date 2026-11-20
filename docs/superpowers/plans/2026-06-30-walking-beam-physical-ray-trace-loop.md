# Walking-Beam Physical Ray Trace Loop Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the current walking-beam storyboard prototype with a reusable finite-aperture ray-traced model that can drive the Blender scene and produce physically plausible beam-walking movies.

**Architecture:** The import-safe physical model will live under `simulations/blender/altair_blender/` and will own rays, plane mirrors, circular apertures, interactions, trace results, and alignment states. The Blender scene will become a renderer of trace results: it will not invent beam path coordinates independently from the physical trace.

**Tech Stack:** Python 3.13, pytest, Black, ruff, basedpyright where practical, Blender Python for rendering, ffmpeg for movie/contact-sheet review.

---

## Loop Rules

- Stay on `codex/walking-beam-alignment-quality-loop`.
- Make one detailed commit per iteration.
- Use TDD for behavioral changes.
- Keep reusable physics helpers import-safe without Blender.
- Verify with focused tests before every commit.
- Generate and inspect render outputs when the iteration touches visual output.
- Preserve working iterations; discard only failed local changes before commit.

## Iteration 1: Physical Trace Contract Tests

**Files:**
- Modify: `tests/test_walking_beam_scene_contract.py`
- Modify: `tests/test_blender_import_contracts.py`
- Possibly create: `tests/test_walking_beam_physics.py`

- [ ] Add failing tests proving the current model must expose finite M1/M2 hit validity.
- [ ] Add failing tests for "no downstream beam after missed mirror".
- [ ] Add failing tests for finite beam footprint clearance through iris apertures.
- [ ] Run focused tests and capture expected failures.
- [ ] Implement only enough placeholders/types if needed to make the test import path explicit.
- [ ] Commit.

## Iteration 2: Reusable Ray/Element Primitives

**Files:**
- Create or modify: `simulations/blender/altair_blender/beam_walking.py`
- Modify: `tests/test_walking_beam_physics.py`

- [ ] Add `Ray3D`, `PlaneMirror`, `CircularAperture`, `RayInteraction`, and `RayTraceResult`.
- [ ] Implement vector reflection and finite circular-aperture hit tests.
- [ ] Verify mirror hits report local coordinates, clear-aperture margin, and status.
- [ ] Commit.

## Iteration 3: Physical Walking-Beam Layout

**Files:**
- Modify: `simulations/blender/altair_blender/beam_walking.py`
- Modify: `simulations/blender/scenes/walking_beam_alignment.py`
- Modify: `tests/test_walking_beam_scene_contract.py`

- [ ] Build a reusable `BeamWalkingLayout` from source-backed prescriptions and scene transforms.
- [ ] Ensure initial and aligned states hit M1 and M2 inside finite apertures.
- [ ] Remove independent `mirror_surface_offset_mm` assumptions where practical.
- [ ] Commit.

## Iteration 4: Physical Mirror Adjuster States

**Files:**
- Modify: `simulations/blender/altair_blender/beam_walking.py`
- Modify: `simulations/blender/scenes/walking_beam_alignment.py`
- Modify: `tests/test_walking_beam_physics.py`

- [ ] Replace abstract `m1_offset_mm` behavior with mirror pitch/yaw perturbations or a compatibility layer that produces physical mirror normals.
- [ ] Verify factor-of-two reflected-angle response for mirror tilt.
- [ ] Commit.

## Iteration 5: Trace-Driven Beam Segments

**Files:**
- Modify: `simulations/blender/scenes/walking_beam_alignment.py`
- Modify: `tests/test_walking_beam_scene_contract.py`

- [ ] Replace hand-built folded/downstream paths with trace-produced beam segments.
- [ ] Hide or shorten beams at first missed mirror/aperture interaction.
- [ ] Commit.

## Iteration 6: Trace-Driven Iris Footprints

**Files:**
- Modify: `simulations/blender/scenes/walking_beam_alignment.py`
- Modify: `simulations/blender/altair_blender/geometry.py` if planar spot helpers are needed.
- Modify: tests.

- [ ] Replace floating iris spot markers with trace-derived planar footprints.
- [ ] Represent pass, block, and partial clipping states explicitly.
- [ ] Commit.

## Iteration 7: More Realistic Iterative Alignment Sequence

**Files:**
- Modify: `simulations/blender/altair_blender/beam_walking.py`
- Modify: `simulations/blender/scenes/walking_beam_alignment.py`
- Modify: tests.

- [ ] Generate a sequence where M1 mainly improves Iris 1 and M2 mainly improves Iris 2.
- [ ] Ensure residual errors decrease but are not magically exact until final hold.
- [ ] Commit.

## Iteration 8: Diagnostics And Review Outputs

**Files:**
- Modify: `simulations/blender/scripts/render_walking_beam_alignment.sh`
- Modify: `simulations/blender/scenes/walking_beam_alignment.py`
- Modify: tests.

- [ ] Add trace diagnostics suitable for quick review.
- [ ] Add or improve contact-sheet generation paths if missing.
- [ ] Commit.

## Iteration 9: Draft Render Review

**Files:**
- Modify as required by visual findings.

- [ ] Run a draft render or a short smoke render.
- [ ] Generate contact sheets.
- [ ] Inspect visible mirror hits, iris blocking, captions, and camera framing.
- [ ] Fix observed issues with tests when possible.
- [ ] Commit.

## Iteration 10: Final Polish And Push

**Files:**
- Modify docs/tests/scripts as needed.

- [ ] Update README/AGENTS/docs with final run instructions and fidelity boundaries.
- [ ] Run focused tests and broad simulation checks.
- [ ] Push the branch.
- [ ] Commit final polish.

