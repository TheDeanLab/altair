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

## Render Movies

Use the render script to create the `.blend` file, both camera-view PNG
sequences, both camera-view MP4 movies, a vertically stacked PNG sequence, and a
stacked MP4 movie:

```bash
simulations/blender/scripts/render_achromat_back_reflection.sh
```

By default, outputs are written under `output/achromat_back_reflection/`:

```text
achromat_back_reflection.blend
frames/wide/frame_0001.png ...
frames/card_closeup/frame_0001.png ...
frames/stacked/frame_0001.png ...
achromat_back_reflection_wide.mp4
achromat_back_reflection_card_closeup.mp4
achromat_back_reflection_stacked.mp4
```

For a faster smoke render, override the frame range and resolution:

```bash
FRAME_START=1 FRAME_END=24 RESOLUTION_X=960 RESOLUTION_Y=540 \
  simulations/blender/scripts/render_achromat_back_reflection.sh output/smoke
```

Run a dry-run plan without invoking Blender or `ffmpeg`:

```bash
simulations/blender/scripts/render_achromat_back_reflection.sh --dry-run
```

## Test

Run non-Blender checks from the repository root:

```bash
uv run pytest tests/test_blender_optics_math.py tests/test_blender_import_contracts.py tests/test_achromat_scene_contract.py tests/test_blender_render_script.py
```

If `uv run` is not suitable in the local environment, use:

```bash
pytest tests/test_blender_optics_math.py tests/test_blender_import_contracts.py tests/test_achromat_scene_contract.py tests/test_blender_render_script.py
```
