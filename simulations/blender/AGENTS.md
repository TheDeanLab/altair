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
- For the AC254-100-A achromat scene, use `prescriptions.py` as the source of
  truth for lens and LMR1-style mount dimensions. The mounted-lens and mount
  drawing dimensions are official Thorlabs data; the AC-series surface
  prescription is used as a documented geometric teaching model.
- Back-reflection spots should come from ray-bundle helpers when possible, not
  hand-positioned offsets. Keep those helpers import-safe without Blender.
- The current ray model traces geometric surface reflections but does not model
  wavelength-dependent refraction through the cemented doublet or coating
  Fresnel coefficients.
- The walking-beam scene now uses one continuous finite-aperture geometric ray
  chain from laser to M1 to M2 to Iris 1 to Iris 2. Animated beam segments, iris
  spots, blocking, and mirror display rotations should remain derived from that
  trace.
- Walking-beam beam objects are five stable trace-derived display slots:
  `incoming`, `m1_to_m2`, `m2_to_iris1`, `iris1_to_iris2`, and `post_iris2`.
  Do not replace them with hand-positioned special-case geometry.
- Animated traced beams should use `optics.create_beam_curve_between` and
  `optics.keyframe_beam_curve_between` so start and end points are constrained
  directly. Avoid sparse Euler-rotated cylinders for propagated beams because
  Blender can interpolate through an equivalent but visually wrong rotation.
- Walking-beam animation uses sampled physical trace states between the six
  caption/storyboard milestones. Keep captions tied to the named milestones,
  but recompute beam geometry, mirror footprints, and iris spots from sampled
  traces for smoother motion.
- Walking-beam storyboard states still use an abstract target-offset model for
  the teaching sequence, but `beam_walking.solve_two_mirror_alignment` converts
  those targets into physical M1/M2 pitch-yaw adjustments. Do not reintroduce
  hand-positioned beam segments or mirror rotations that bypass the solver.
- Walking-beam iris visuals distinguish `passed`, `clipped`, `blocked`, and
  `not_reached` states. Clipped downstream power is intentionally dimmed and
  represented as a larger spot; reticles should stay muted and front-only so
  they do not read as beam spots.
- Kinematic mirror optics should appear flush with the front face of the mirror
  mount. The physical ray-trace surface remains the optic reference plane; the
  mount frame should sit behind that plane.
- The default walking-beam misalignment is intentionally moderate: gross
  alignment clips/stops at Iris 1, M1 centers Iris 1, M2 reaches and centers
  Iris 2, then two refinements converge. Larger errors may be physically valid,
  but can hide downstream tutorial targets behind upstream apertures.
- Use minimal in-scene labels for teaching videos when they clarify the setup.
  Keep labels unobtrusive and reusable through `geometry.create_scene_label`.

## Run Pattern

Run a scene from the repository root with Blender:

```bash
blender --background --python simulations/blender/scenes/achromat_back_reflection.py
```

Render deliverable movies with the scene-specific script:

```bash
simulations/blender/scripts/render_achromat_back_reflection.sh
```

That script intentionally creates the `.blend` file, renders PNG frame
sequences first, then encodes MP4 movies with `ffmpeg`. This is more reliable
than direct Blender movie output in the currently verified Blender 5.1
background runtime.

The achromat script preserves the wide, card close-up, and stacked movies and
adds a hero movie. Its default render mode is `final` for Cycles output; use
`--draft` for card-only timing checks, and use `--preview` or
`RENDER_MODE=preview` for full-pipeline EEVEE iteration.
Keep the render preset machinery in `altair_blender.scene` reusable for future
videos instead of hard-coding engine settings in scene scripts.

For walking-beam renders, use
`simulations/blender/scripts/render_walking_beam_alignment.sh`. Full and
preview runs emit wide, iris close-up, hero, top-down, and stacked movies.
Draft mode intentionally renders only the iris close-up timing check. Use
`simulations/blender/scripts/render_walking_beam_alignment_stills.sh` for quick
contact-sheet review of key frames; the stacked still combines wide, iris
close-up, and top-down views.

In the verified Blender 5.1.2 runtime, `CYCLES` can be assigned as
`scene.render.engine` even when the render-engine enum list only reports
`BLENDER_EEVEE`. Do not use the enum list alone to decide whether Cycles is
available.

If Blender is not on `PATH`, document that limitation and run the non-Blender
pytest checks.

## Code Style

- Keep modules import-safe without Blender. Import `bpy` lazily inside functions
  that need it.
- All Python functions and methods in `simulations` should have explicit type
  hints and numpydoc-style docstrings. Include `Parameters`, `Returns`, or
  `Yields` sections when they apply.
- Run Black on simulation Python files after edits.
- Put reusable helpers in `altair_blender/`.
- Put scene-specific timelines in `scenes/`.
- Put repeatable render/export workflows in `scripts/`.
- Keep source-backed physical constants in `prescriptions.py`.
- Prefer explicit names over clever abstractions.
- Keep visual approximation constants visible near the top of scene scripts.
