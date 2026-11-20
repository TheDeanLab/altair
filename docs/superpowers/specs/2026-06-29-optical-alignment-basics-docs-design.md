# Optical Alignment Basics Documentation Design

## Goal

Create a canonical documentation page for the general back-reflection alignment
method used to align individual optics in a collimated laser beam. The page
should explain the purpose of the method, show the first Blender simulation
movie, and provide protocol-like directions that can be reused across Altair
systems.

## Placement

Add a new first-section documentation page:

```text
docs/source/getting_started/optical_alignment_basics.rst
```

Add the page to the first `docs/source/index.rst` toctree under the general
Table of Contents. It should appear near the existing introduction, required
software, hardware, and getting-started entries because the method is a general
alignment skill rather than a build-specific instruction.

The page title should be:

```text
Basics of Optical Alignment
```

## Video Asset

Embed the existing tracked stacked movie:

```text
docs/source/_static/baseplate2_alignment/alignment/videos/achromat_back_reflection_stacked.mp4
```

Use the existing Sphinx raw-HTML video pattern already present in the repository.
The raw HTML video block must be accompanied by a normal RST fallback link to
the MP4 so the movie is still reachable outside normal HTML playback. The new
page becomes the canonical home for the video. The existing `baseplate2_alignment`
Step 7 section should keep a short contextual card and link to the new canonical
page instead of duplicating the full explanation.

## Page Content

The page should be protocol-like and explicit about the purpose of the method.
It should include these sections:

1. **Goal**
   - Align the optic so the incident beam is centered on the optic and normal to
     the optic.
   - Use the back-reflection spots on an aperture card as a sensitive alignment
     readout.

2. **Why This Works**
   - A standard lens in a beam path reflects light from multiple optical
     surfaces, commonly the front and rear surfaces.
   - Flat or nearly plano surfaces tend to return crisp, collimated spots
     similar in diameter to the incoming beam.
   - Spherical or curved surfaces can return spots that expand or focus,
     depending on surface curvature and spacing.
   - For achromats and compound optics, different surfaces can produce
     reflection spots with different diameters.

3. **Setup**
   - Use a visible, low-power, collimated alignment beam.
   - Place a business card or target card with a small aperture in the beam.
   - Center the aperture on the beam before inserting the optic.
   - Place the optic in its mount downstream of the card.
   - Observe the return spots on the card surface.

4. **Interpreting Reflection Spots**
   - If the beam is not centered on the optic, the back-reflection spots are
     displaced on the card.
   - Lateral optic displacement moves the return spots laterally.
   - Vertical optic displacement also moves the return spots on the card because
     the card is read in its local transverse coordinates.
   - When the beam is normal to the optic, the return spots should be displaced
     symmetrically.
   - When the optic is tilted relative to the laser propagation direction, the
     return spots are not displaced symmetrically.
   - The aperture card is part of the measurement. If the aperture is not
     centered on the true beam path, the measurement can be misleading.

5. **Step-By-Step Protocol**
   - Establish a clean collimated alignment beam.
   - Place the aperture card in the beam and center the aperture on the beam.
   - Insert the optic and observe the return reflections.
   - Correct angular alignment first until the reflections move symmetrically
     toward the aperture.
   - Correct lateral and vertical position until the relevant reflections are
     centered on the aperture.
   - Iterate angle and position adjustments because they are coupled.
   - Confirm the result by translating the card slightly along the beam path and
     checking that the spot behavior remains consistent.

6. **Complex Optics**
   - Objectives and other multi-element assemblies can produce many return
     reflections.
   - The operator should identify the reflections that are meaningful for the
     alignment step instead of trying to center every ghost reflection.
   - The basic principle remains the same: useful reflection spots should return
     toward the aperture when the optic is centered and normal to the beam.

## Cross-Linking

Update `docs/source/baseplate2_alignment/baseplate2_alignment.rst` Step 7 so it
refers readers to the new general page for the method. Keep the baseplate page
focused on the RFO-specific alignment context.

## Verification

After implementation, run:

```bash
uv run --frozen pytest tests/test_docs.py
```

If the full docs linkcheck still fails because of pre-existing external links,
also run a local HTML build or a targeted Sphinx build that verifies the new page
renders and the video path resolves.

## Out Of Scope

- Generating a new movie.
- Replacing the existing baseplate-specific alignment protocol.
- Adding narration, audio, or external video-hosting infrastructure.
- Claiming the Blender simulation is an exact optical design solver.
