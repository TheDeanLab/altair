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
`--preview` or `RENDER_MODE=preview` for fast EEVEE iteration and smoke tests.
Keep the render preset machinery in `altair_blender.scene` reusable for future
videos instead of hard-coding engine settings in scene scripts.

In the verified Blender 5.1.2 runtime, `CYCLES` can be assigned as
`scene.render.engine` even when the render-engine enum list only reports
`BLENDER_EEVEE`. Do not use the enum list alone to decide whether Cycles is
available.

If Blender is not on `PATH`, document that limitation and run the non-Blender
pytest checks.

## Code Style

- Keep modules import-safe without Blender. Import `bpy` lazily inside functions
  that need it.
- Put reusable helpers in `altair_blender/`.
- Put scene-specific timelines in `scenes/`.
- Put repeatable render/export workflows in `scripts/`.
- Keep source-backed physical constants in `prescriptions.py`.
- Prefer explicit names over clever abstractions.
- Keep visual approximation constants visible near the top of scene scripts.
