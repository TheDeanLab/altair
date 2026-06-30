# Walking-Beam Alignment Physical Accuracy Audit

This audit documents why the first-pass walking-beam alignment render was not a
physically faithful model of the two-mirror, two-iris alignment procedure. It is
kept as historical design context and as a checklist for future review passes.

## Current Branch Status

The current PR draft branch has replaced the first-pass manual beam animation
with a finite-aperture geometric ray chain and a reusable physical mirror
solver:

- `altair_blender.beam_walking` contains import-safe 3D ray, mirror, aperture,
  trace, and two-mirror solver helpers.
- `scenes/walking_beam_alignment.py` derives folded/downstream beam cylinders,
  iris spot positions, spot visibility, blocking state, and mirror display
  rotations from the physical trace.
- The default tutorial sequence is now tuned to be physically reachable by the
  modeled KM100CP mirror aperture and 2.5 mm iris apertures.

Current traced storyboard summary:

| State | First block | Iris 1 radius | Iris 2 radius | Teaching role |
| --- | --- | ---: | ---: | --- |
| `gross_misalignment` | Iris 1 | 1.793 mm | not reached | Initial beam clips/stops at the near iris. |
| `m1_centers_iris1` | Iris 2 | 0.000 mm | 2.505 mm | M1 correction centers the near iris. |
| `m2_centers_iris2` | none | 0.939 mm | 0.000 mm | M2 correction reaches and centers the far iris while perturbing Iris 1. |
| `m1_refinement` | none | 0.000 mm | 0.024 mm | M1 refinement recenters the near iris with small far residual. |
| `m2_refinement` | none | 0.000 mm | 0.000 mm | M2 refinement removes the remaining far residual. |
| `aligned_hold` | none | 0.000 mm | 0.000 mm | Final hold with both iris spots centered. |

Remaining limitations:

- This is still geometric ray tracing, not Gaussian beam propagation or wave
  optics.
- Iris clipping is modeled as a simple finite-radius beam/aperture interaction,
  not a diffraction pattern or realistic partial-beam spot shape.
- Mirror knobs are represented as pitch/yaw angles rather than screw turns or a
  full kinematic mount mechanism.
- Intermediate animation frames are Blender interpolation between ray-traced
  keyframes; future work could sample every rendered frame through the solver.

## Latest Render Review: 2026-06-30

The latest rendered movies reviewed were:

- `/Users/Dean/Downloads/walking_beam_alignment_wide.mp4`
- `/Users/Dean/Downloads/walking_beam_alignment_hero.mp4`
- `/Users/Dean/Downloads/walking_beam_alignment_stacked.mp4`
- `/Users/Dean/Downloads/walking_beam_alignment_iris_closeup.mp4`

Representative frames confirm several visual defects that remain after the
first physical-trace pass:

| Defect | Observed behavior | Likely source in the current scene |
| --- | --- | --- |
| Rectangular glow at M1 | The first mirror shows a bright rectangular/slot-like feature instead of a circular beam footprint. | The ray-traced mirror plane uses the mount origin, while the visible mirror optic is offset inside the KM100CP visual model. The beam endpoint and mirror mesh are therefore not the same physical surface. |
| Hidden M1-to-M2 beam | The folded beam segment is weak or partly hidden, especially in the hero view. | The scene renders only one animated folded cylinder and one downstream cylinder, with no segment-specific visual diagnostics or camera guarantee that the folded path is visible. |
| Ambiguous M2 direction | In the hero movie the downstream beam can read as if it is coming from the wrong side of M2. | The hero camera is nearly collinear with the downstream path and does not show enough of the Z-fold geometry. A top-down/oblique path camera is needed. |
| Glowing iris ring | The iris ring/ticks can be mistaken for a laser spot. | `create_post_mounted_iris` uses the emissive `alignment_reference` material on both reticle faces, while beam spots are also emissive and similarly colored. |
| Spot/clip fidelity | Iris clipping is hard to distinguish from a centered pass. | `create_return_spot` creates one flattened emissive sphere per iris; the visual does not encode passed, clipped, and blocked interactions distinctly. |

The current physical trace still has a coherent segment order:

```text
source -> M1 -> M2 -> Iris 1 -> Iris 2 -> downstream
```

For example, frame 72 (`m2_centers_iris2`) traces M1 and M2 hits, clips Iris 1,
passes Iris 2, and halves the downstream power. The visual system does not yet
make those distinctions obvious enough for a teaching movie.

## Reference Procedure

Standard beam walking uses two steering mirrors upstream of two same-height
irises. The desired beam path is the straight line through the two iris centers.
The upstream mirror is adjusted to correct the beam position at the near iris,
and the downstream mirror is adjusted to correct the beam angle so the beam
passes through the far iris. Because the two controls are coupled, the operator
alternates between the two mirrors until both iris spots remain centered.

References consulted:

- Thorlabs, "Two steering mirrors can be used to walk a laser beam to a new
  path": https://www.thorlabs.com/two-steering-mirrors-can-be-used-to-walk-a-laser-beam-to-a-new-path
- Berkeley Experimentation Lab mini-project report:
  https://experimentationlab.berkeley.edu/sites/default/files/Mini-Project%20Report.pdf
- Virtual Etters, "Walking the beam":
  https://virtualetters.blogspot.com/2012/07/walking-beam.html
- Stony Brook laser mini-project draft:
  http://www.stonybrook.edu/laser/_simone/abstracts/mini-projectdraft.html

## High-Level Verdict

The current animation communicates the rough idea of alternating between two
mirrors, but the rendered beam is not a physically constrained ray path. The
scene mixes three different models:

1. A nominal static Z-fold traced from infinite mirror planes.
2. A two-axis algebraic iris-offset model that does not trace mirror
   reflections.
3. Blender beam cylinders and spots that are manually keyframed from those
   offsets.

Those models are not solved together. As a result, the movie can show a beam
after a mirror it never physically hit, a beam continuing after an iris should
block it, and mirror rotations that are visually disconnected from the ray
geometry.

## Quantitative Failures In The Current Scene

These values were computed from the current branch defaults in
`scenes/walking_beam_alignment.py` and the source-backed KM100CP clear aperture
in `prescriptions.py`.

### The Nominal Beam Misses M1

The nominal M1 surface hit is:

```text
world hit: (-40.901, -31.001, 45.800) mm
M1 local transverse radius from mirror center: 21.000 mm
KM100CP modeled clear-aperture radius: 11.950 mm
```

The ray therefore starts outside the first mirror aperture. A physical beam
would not reflect into the rest of the scene. This matches the visible defect
where the incoming beam appears to miss the mirror/mirror optic.

### Early States Miss M2 But Still Draw A Downstream Beam

The current M2 hit point is state-dependent. The first three storyboard states
place that hit outside the modeled M2 clear aperture:

| State | M2 local transverse radius | Inside 11.95 mm clear aperture? |
| --- | ---: | --- |
| `gross_misalignment` | 14.308 mm | No |
| `m1_centers_iris1` | 18.578 mm | No |
| `m2_centers_iris2` | 19.715 mm | No |
| `m1_refinement` | 6.903 mm | Yes |
| `m2_refinement` | 6.895 mm | Yes |
| `aligned_hold` | 7.000 mm | Yes |

For the first three states, a real beam should stop at, miss, or clip M2. The
movie instead still draws an animated beam after M2 and iris spots. This is the
largest physical error in the current render.

### Iris Blocking Uses Beam Center, Not Full Beam Footprint

The current blocking logic checks whether the beam center is inside the iris
radius. A finite 1 mm beam should pass only when:

```text
center offset + beam radius <= aperture radius
```

The current aperture radius is 1.25 mm and the physical beam radius is 0.50 mm.
Center-only tests are too permissive near the iris edge. Future code should
distinguish between:

- center hits inside aperture,
- full beam clears aperture,
- partial clipping,
- full blockage by the iris leaf/body.

The animation should show clipped or crescent-shaped spots when the beam
partially intersects an iris, not only binary on/off spots.

## Procedure-Level Inaccuracies

### The Beam Should Be A Continuous Ray Chain

The physical chain is:

```text
laser source -> M1 finite mirror -> M2 finite mirror -> Iris 1 aperture
-> Iris 2 aperture -> downstream output
```

Every segment should be generated from the previous interaction. If the beam
misses M1, there is no M1-to-M2 segment. If it misses M2, there is no
downstream segment. If it clips Iris 1, there is no full beam at Iris 2.

The current code computes a nominal source-to-M1-to-M2 path, then separately
computes downstream iris offsets. Those calculations are not one continuous ray
trace.

### M1 And M2 Adjustments Are Not Mirror Adjustments

`BeamWalkingAxisState.m1_offset_mm` is described as an "M1 correction", but it
is not a physical mirror pitch/yaw angle. It is an abstract transverse offset
term that is converted into a visual mirror rotation using an arbitrary display
scale.

`BeamWalkingAxisState.m2_angle_mrad` is closer to a downstream beam angle, but
it is still not a mirror normal. A real flat mirror changes the reflected beam
angle by twice the mirror tilt, and the reflected direction must be computed
from the incident direction and mirror normal.

The future model should store mirror adjuster states as physical pitch/yaw
angles or screw turns. Beam position and angle should then emerge from specular
reflection.

### The Animation Does Not Enforce The Law Of Reflection Per State

For each storyboard state, the rendered folded beam is constructed from:

```text
fixed M1 surface point -> synthetic M2 start point inferred from iris offsets
```

That segment is not produced by reflecting the incoming beam from the animated
M1 normal. Similarly, the downstream segment is not produced by reflecting the
folded beam from the animated M2 normal.

This allows impossible states where:

- the beam start point remains fixed while M1 visibly rotates,
- the M2 hit point moves without being caused by an M1 reflection,
- the downstream beam exists even when the M2 hit is outside the mirror,
- mirror rotations and beam motion disagree.

### The Mirror Geometry Is Treated As Infinite Planes

The nominal fold is traced using mirror planes, but finite mirror radii are not
part of the trace. The current branch added finite mirror and iris geometry for
rendering, but the displayed ray is not clipped by those finite surfaces.

For a physically credible teaching movie, every mirror intersection must report:

- hit/miss,
- local mirror coordinates,
- clear-aperture margin,
- reflected direction,
- whether the beam footprint is fully reflected, partially clipped, or lost.

### The Current Layout Does Not Respect The Visual Hardware

The ray plane point is controlled by `mirror_surface_offset_mm`, while the mirror
mesh surface is built separately from KM100CP dimensions. These should not be
independent magic numbers. The geometric mirror surface used for ray tracing
should be derived from the same prescription and transform that build the mesh.

The current M1 hit is outside the mirror optic even before any iterative
alignment starts. A correct layout should place the initial beam on both mirror
surfaces, even if it is badly misaligned at the irises.

### The M2-To-Iris Geometry Is Too Abstract

The downstream algebra assumes offsets at Iris 1 and Iris 2 are enough to
describe the post-M2 beam. That is true for a straight line after M2, but it
does not explain how the line was produced by M2. The future model should
derive the downstream line from the M2 reflection, then evaluate that line at
the iris planes.

### Horizontal And Vertical Axes Are Over-Separated

The current model treats horizontal and vertical alignment as independent scalar
problems. In a real Z-fold, mirror pitch and yaw are transformed by the fold
geometry. A horizontal knob on one mirror does not always map to the same world
axis after one or two reflections, and vertical tilt can change the local hit
position on the downstream mirror.

The future implementation should represent rays and mirror normals as 3D
vectors and use vector reflection for both axes.

## Animation And Storyboard Inaccuracies

### The Initial State Is Not A Plausible Beam-Walking Starting Point

The label says "Start: beam misses both irises", which can be a reasonable
coarse-alignment state. But a beam-walking tutorial should still start after
the beam has been found on both steering mirrors. In the current movie, the
beam misses M1 and early states miss M2. That is not a beam-walking procedure;
it is an unestablished optical path.

A better initial state is:

- beam hits M1 within the mirror aperture,
- reflected beam hits M2 within the mirror aperture,
- beam reaches the iris row but is off-center or clips the first iris,
- both mirror adjusters have visible but small physical errors.

### Keyframes Are Not Ray-Traced States

The storyboard states are computed with an algebraic iris-offset model. The
beam cylinders and spots are then keyframed to those values. Intermediate frames
are linear interpolations of Blender object transforms, not ray-traced optical
states.

This can create intermediate frames in which the visible beam cuts through
hardware or violates reflection geometry. Every keyframe, and ideally every
sampled animation frame, should be generated by the same ray-tracing function.

### The Process Is Too Perfect And Too Discrete

The current sequence solves the near or far iris analytically at each step and
then jumps to an exact final alignment state. Real beam walking is iterative:
adjustments are partial, one mirror correction perturbs the other iris, and the
operator repeats smaller corrections.

The storyboard should show residual errors decreasing over iterations, not only
ideal "center Iris 1" and "center Iris 2" states.

### Mirror Rotations Are Display Exaggerations, Not The Cause Of Alignment

The mirror objects rotate for visual feedback, but the rotations do not drive
the ray path. The path drives the visual rotations. This reverses causality.

The future model should compute:

```text
mirror adjuster state -> mirror normal -> reflected ray -> iris intercepts
```

The render should never compute:

```text
desired iris intercept -> visual ray -> unrelated mirror rotation
```

### The Irises Are Fixed At A Narrow Opening Throughout

The docs correctly note that a real operator usually starts with larger iris
openings and closes them as alignment improves. The current movie uses one
fixed narrow display aperture. That makes the initial state visually confusing
and encourages impossible "beam through iris" artifacts.

The simulation should optionally animate the iris apertures:

1. large enough for coarse acquisition,
2. smaller during refinement,
3. final working aperture for the aligned hold.

### The Close-Up View Can Be Misleading

The close-up and hero views often show a bright line passing near or through an
iris without clearly showing whether the beam is blocked by the front face,
passes through the aperture, or clips the aperture. The current spot markers
are glowing spheres, not physically clipped beam footprints.

The final video should show:

- front-face spot when blocked,
- transmitted beam only when the aperture clears the full beam footprint,
- clipped footprint shape when partially blocked,
- no downstream spot if the upstream iris blocks the beam.

## Rendering And Visual Inaccuracies

### Beam Cylinders Are Geometry, Not Light Transport

The green beam is a glowing cylinder mesh, not a ray that interacts with scene
geometry. It does not cast a physically meaningful footprint on mirrors or
iris leaves. It can visually pass through an object if the manually chosen end
point and camera angle make it look continuous.

The next version can still use beam meshes for readability, but those meshes
must be generated from a physical trace result.

### Spots Are Not Oriented Or Clipped To Iris Planes

The current iris spots are generated with the back-reflection spot helper and
placed as small spheres near each iris face. A real alignment spot is a beam
footprint on a planar iris face or aperture edge. It should be a disk or clipped
disk oriented on the iris plane, not a sphere floating near the iris.

### Visual Exaggeration Is Applied To Beam Paths

`beam_path_offset_exaggeration` and `spot_display_exaggeration` scale the
rendered offsets relative to physical offsets. This can be useful for teaching,
but it should not be mixed with physical hit tests or hardware intersections.

Future code should keep two layers:

- physical coordinates used for all ray/hit/blocking decisions,
- optional display offsets used only after trace validity is known.

When exaggeration is enabled, the scene should make clear that the displayed
offsets are magnified.

### There Is No Beam Diameter Propagation Model

The current model treats the beam as a fixed-radius cylinder. For this tutorial,
a collimated fixed-diameter beam is acceptable, but the model still needs
finite-footprint clipping at apertures and finite mirror footprints. It does
not need Gaussian propagation at first, but it should not treat the beam as a
zero-width centerline for blocking.

### No Power Or Visibility Accounting Exists

The movie does not track whether a beam segment has nonzero transmitted power.
If M1 or M2 is missed, downstream power should be zero. If an iris clips the
beam, downstream power should be reduced or zero depending on the clipping.

Even a simple binary/area-overlap model would be more physically meaningful
than the current hand-hidden spots.

## Code Architecture Issues Blocking A High-Fidelity Fix

### The Beam-Walking Math Is Too Scene-Specific

`altair_blender/beam_walking.py` is import-safe, which is good, but its current
model is not a general ray tracer. It encodes a special two-axis linear model
for two irises and two mirrors. That will not scale to other optical alignment
videos.

The next version should introduce reusable primitives:

- `Ray3D`: origin, unit direction, beam radius, wavelength, power.
- `PlaneMirror`: transform, clear aperture, finite optic radius, reflectivity.
- `CircularAperture`: plane, aperture radius, body radius, thickness.
- `RayInteraction`: hit point, local coordinates, surface name, status.
- `RayTraceResult`: ordered interactions, beam segments, blocked reason.
- `BeamWalkingLayout`: source, mirrors, irises, target line.
- `AlignmentStep`: name, frame, mirror adjuster values, trace result.

### Geometry And Ray Tracing Use Separate Source Data

Mesh builders and ray-tracing helpers should consume the same prescriptions and
transforms. A mirror cannot be visually at one surface while ray tracing uses a
different plane.

The future implementation should build a scene graph or lightweight component
records first, then use those records both to:

1. create Blender objects,
2. trace rays and validate intersections.

### Tests Verify Storyboard Intent, Not Physical Validity

The current tests check that:

- named states exist,
- errors decrease,
- iris points move as expected,
- nominal mirror planes are intersected.

They do not require:

- M1 hit within finite mirror aperture,
- M2 hit within finite mirror aperture for every rendered downstream beam,
- reflected direction equals vector reflection from the animated mirror normal,
- no beam segment after a missed mirror,
- no downstream segment after a blocking iris,
- finite beam footprint clears aperture before passing,
- displayed spots are absent or clipped when the beam is blocked.

Those should become contract tests before refactoring the render.

## Required Acceptance Criteria For The Fix

The next walking-beam implementation should satisfy these criteria.

### Geometry

- The laser source, M1, M2, Iris 1, and Iris 2 are defined as reusable component
  records with physical transforms and apertures.
- The initial beam hits both mirrors inside their clear apertures.
- Every mirror hit reports local coordinates and clear-aperture margin.
- Every iris interaction reports center offset, full-beam clearance, and
  clipping/blocking status.
- The rendered beam never continues past the first missed or blocking element.

### Physics

- Mirror reflection uses vector reflection from incident direction and mirror
  normal.
- Mirror adjustment states are physical pitch/yaw values or screw-turn values.
- Beam-angle changes obey the factor-of-two mirror tilt relationship.
- The downstream beam after M2 is derived from the M2 reflection, not directly
  from desired iris offsets.
- Iris pass/fail uses the full beam radius, not only the centerline.

### Alignment Procedure

- The starting state is misaligned at the irises but still physically reaches
  both steering mirrors.
- M1 correction primarily improves the near iris and leaves a residual far-iris
  error.
- M2 correction primarily improves the far iris and perturbs the near iris.
- The sequence alternates between M1 and M2 with decreasing residual errors.
- The final state passes through both iris apertures with a positive aperture
  margin.

### Rendering

- Beam cylinders are generated only from successful physical trace segments.
- Blocked beams terminate at the blocking mirror or iris face.
- Iris spots are planar footprints on the appropriate face, not floating
  spheres.
- Partial clipping is shown explicitly or at least reported in the trace result.
- Visual exaggeration is optional and isolated from physical calculations.
- The camera views make M1, M2, both irises, and the relevant blocked/pass
  status unambiguous.

### Reusability

- The ray-tracing and alignment-state code lives in import-safe helpers under
  `altair_blender/`.
- The Blender scene script only maps trace results to geometry, materials,
  keyframes, and cameras.
- Tests cover the import-safe physical model without requiring Blender.
- The render script remains a reusable movie pipeline rather than a one-off.

## Suggested Implementation Plan

1. Add import-safe geometric primitives for rays, plane mirrors, and circular
   apertures.
2. Write failing tests that reproduce the current M1 and M2 aperture misses.
3. Replace the algebraic iris-offset model with sequential tracing:

   ```text
   source ray -> M1 -> M2 -> Iris 1 -> Iris 2 -> downstream
   ```

4. Define mirror adjuster states as pitch/yaw values. Generate alignment states
   from those values.
5. Implement a simple control loop for the teaching sequence:
   M1 partial correction, M2 partial correction, repeat, final hold.
6. Generate Blender beam segments and iris footprints from the trace result.
7. Add contract tests for finite mirror hits, aperture blocking, and trace
   continuity.
8. Re-render the four movie views and inspect contact sheets before publishing.

## Current Video-Specific Observations

- In the wide and stacked views, the incoming beam appears offset from the M1
  optic instead of clearly striking its reflective surface.
- The first three storyboard states display a downstream beam even though the
  computed M2 hit is outside the modeled clear aperture.
- In the iris close-up view, the beam can read as passing through an iris even
  when the state says it is blocked, because the beam cylinder and spot marker
  are hand-positioned visual objects.
- The hero view often crops out the downstream mirror while captions discuss M2
  adjustment, making it harder to see the physical cause of the beam motion.
- The final aligned state is visually plausible, but it does not prove the
  preceding states were physically reachable.

## Bottom Line

The current movie should be treated as a storyboard prototype only. It is not
yet a physically faithful beam-walking simulation. The next version should be
built around one continuous, reusable ray-tracing model with finite mirror and
aperture interactions, then render only the segments and spots produced by that
trace.
