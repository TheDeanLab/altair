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
back-reflection spots return to the card. The animation shows separate
ray-traced alignment states: rotation correction moves both spots together,
horizontal translation splits and recenters the spots left/right, vertical
translation splits and recenters the spots up/down, and final alignment centers
both return spots on the aperture.

The model is intentionally hybrid: it is geometrically plausible and uses
teaching-scale dimensions, but it exaggerates small alignment errors so the
motion is legible in video. The lens is represented as an AC254-100-A-style
cemented doublet with separate N-BK7 and SF5 elements, a curved cemented
interface, a weakly curved rear surface, and an LMR1-style fixed mount. Return
spots are computed from geometric ray-bundle reflections and therefore have
surface-dependent positions and diameters.

The scene includes three camera views: a wide setup view, a close-up view of the
card aperture and return spots, and a slow hero camera move for a polished
single-view movie. Minimal in-scene labels identify the aperture card, doublet,
mount, and two return reflections without adding narration or external editing.

## Walking-Beam Scene

`scenes/walking_beam_alignment.py` generates a teaching scene for walking a
laser beam with two steering mirrors and two irises. The scene uses an
import-safe finite-aperture ray trace from the source through M1, M2, Iris 1,
and Iris 2. Beam segments, mirror footprints, iris spots, blocking/clipping
state, and mirror display rotations are derived from that trace.

The tutorial sequence starts misaligned, uses M1 to center the near iris, uses
M2 to center the far iris, then alternates through two refinements until both
irises are centered. Rendered views include wide, iris close-up, hero, top-down,
and stacked diagnostics. The top-down view is particularly useful for checking
that the folded M1-to-M2 path is continuous and that the post-M2 direction is
unambiguous.

## Fidelity Notes

`altair_blender/prescriptions.py` stores the source-backed model constants. The
mounted AC254-100-A-ML dimensions and LMR1/M mount dimensions come from Thorlabs
drawings. The AC-series surface prescription is used for the educational
geometric model so the rendered doublet and reflected spots respond to surface
curvature.

The spot animation traces reflected ray bundles from selected spherical
surfaces back to the card plane. The optics helpers also include a sequential
geometric tracer that branches rays into reflected and transmitted paths through
all modeled achromat surfaces. The model does not yet include wavelength-
dependent coating reflectance, polarization, diffraction at the aperture, or
Gaussian beam propagation. Spot positions and diameters are physically
motivated, then visually scaled for legibility.

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

## Render Movies

Use the render script to create the `.blend` file, wide/card/hero PNG
sequences, wide/card/hero MP4 movies, a vertically stacked wide-plus-card PNG
sequence, and a stacked MP4 movie:

```bash
simulations/blender/scripts/render_achromat_back_reflection.sh
```

The default render mode is `final`, which applies the Cycles beauty preset. Use
`--draft` for fast card-only timing checks, or `--preview` /
`RENDER_MODE=preview` for full-pipeline EEVEE iteration.

For a fast draft render that only writes the card close-up movie at lower
resolution with frame stepping:

```bash
simulations/blender/scripts/render_achromat_back_reflection.sh --draft output/draft
```

By default, outputs are written under `output/achromat_back_reflection/`:

```text
achromat_back_reflection.blend
frames/wide/frame_0001.png ...
frames/card_closeup/frame_0001.png ...
frames/hero/frame_0001.png ...
frames/stacked/frame_0001.png ...
achromat_back_reflection_wide.mp4
achromat_back_reflection_card_closeup.mp4
achromat_back_reflection_hero.mp4
achromat_back_reflection_stacked.mp4
```

For a faster smoke render, override the frame range and resolution:

```bash
FRAME_START=1 FRAME_END=24 RESOLUTION_X=960 RESOLUTION_Y=540 \
  simulations/blender/scripts/render_achromat_back_reflection.sh --preview output/smoke
```

Run a dry-run plan without invoking Blender or `ffmpeg`:

```bash
simulations/blender/scripts/render_achromat_back_reflection.sh --dry-run
simulations/blender/scripts/render_achromat_back_reflection.sh --draft --dry-run
simulations/blender/scripts/render_achromat_back_reflection.sh --preview --dry-run
```

Render the walking-beam scene with:

```bash
simulations/blender/scripts/render_walking_beam_alignment.sh
```

For key-frame still review:

```bash
simulations/blender/scripts/render_walking_beam_alignment_stills.sh --draft --frame 72 output/walking-beam-frame-72
```

## Test

Run non-Blender checks from the repository root:

```bash
uv run pytest tests/test_blender_optics_math.py tests/test_blender_import_contracts.py tests/test_achromat_scene_contract.py tests/test_blender_render_script.py tests/test_walking_beam_physics.py tests/test_walking_beam_scene_contract.py tests/test_walking_beam_render_script.py
```

If `uv run` is not suitable in the local environment, use:

```bash
pytest tests/test_blender_optics_math.py tests/test_blender_import_contracts.py tests/test_achromat_scene_contract.py tests/test_blender_render_script.py tests/test_walking_beam_physics.py tests/test_walking_beam_scene_contract.py tests/test_walking_beam_render_script.py
```
