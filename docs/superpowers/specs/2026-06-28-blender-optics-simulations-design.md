# Blender Optics Simulations Design

Date: 2026-06-28

## Purpose

Create a reusable Blender Python simulation area in the Altair repository for
educational optics-alignment videos. The first simulation will demonstrate how
to align an achromatic doublet by observing two back-reflection spots on a
business card target with a small aperture.

The first deliverable is a Blender Python scene generator, not a committed
`.blend` file or rendered movie. The script should generate the scene when run
inside Blender and should be structured so future simulations can reuse the
same helper modules.

## Scope

In scope:

- Add a dedicated simulation area under `simulations/blender/`.
- Build a small reusable Python helper package for Blender scene construction.
- Add a local `AGENTS.md` file with subproject context for future agents.
- Add one scene generator for the achromatic-doublet back-reflection demo.
- Use Blender's Python API as the scene-generation interface.
- Use a hybrid teaching model: physically plausible geometry with visual
  exaggeration where needed for clarity.

Out of scope for the first implementation:

- Exact wave-optics simulation.
- Exact Fresnel/refraction modeling.
- Importing Zemax files or manufacturer prescription data.
- Committing rendered movies or generated `.blend` files.
- Building an external command-line application around Blender.

## Repository Layout

The implementation should add:

```text
simulations/
  blender/
    AGENTS.md
    README.md
    altair_blender/
      __init__.py
      animation.py
      cameras.py
      geometry.py
      materials.py
      optics.py
      scene.py
    scenes/
      achromat_back_reflection.py
```

`simulations/blender/AGENTS.md` should be maintained as the local context file
for this subproject. It should record coordinate conventions, scale choices,
run commands, modeling approximations, naming conventions, and durable decisions
that future simulations should preserve.

## First Scene

The first scene will be `simulations/blender/scenes/achromat_back_reflection.py`.
It will generate a clean hybrid view of an optical alignment workflow:

- Simplified optical table and mount references.
- Business card target with a centered aperture of about 1 mm.
- Narrow 561 nm collimated laser beam with about 1 mm diameter.
- Mounted 1 inch achromatic doublet modeled after Thorlabs AC254-100-A-ML
  parameters at the teaching level: 100 mm focal length, visible AR coating,
  and 1 inch mounted optic scale.
- Two visible back-reflection paths from the lens surfaces.
- Two return spots on the business card face.
- Wide camera showing the setup.
- Card close-up camera showing the aperture and return spots.

The scene should be parameterized near the top of the scene script. Parameters
should include beam diameter, wavelength, aperture diameter, lens focal length,
lens diameter, initial tilt, initial decenter, timeline length, and visual
exaggeration.

## Animation Behavior

The default timeline should show a complete alignment story:

1. Opening state: the lens is misaligned; two return spots are displaced from
   the aperture.
2. Tilt correction: the lens angle is adjusted; the return spots move toward
   the aperture.
3. Decenter correction: the lens lateral position is adjusted; the spots become
   more symmetric and centered.
4. Final aligned state: both return spots are centered on the aperture, with a
   brief hold for the viewer.

The back-reflection spot motion should be visually legible. Small physical
tilts and decenters may be scaled for teaching using an explicit exaggeration
parameter. The code and documentation should make clear that this is an
educational geometric model, not a quantitative optical design solver.

## Reusable Modules

`scene.py`:

- Reset the Blender scene.
- Configure units, frame range, render resolution, and basic world lighting.
- Provide safe object-collection helpers.

`materials.py`:

- Create reusable materials for glass, 561 nm laser glow, return spots, matte
  card stock, metal mounts, table surface, and subtle labels.

`geometry.py`:

- Build optical table features, card target, aperture ring, lens barrel,
  simplified achromatic doublet mesh, and basic mount geometry.

`optics.py`:

- Build incident beam and reflected beam visualizations.
- Compute teaching-level return-spot positions from tilt and decenter
  parameters.
- Keep all physical simplifications localized and documented.

`animation.py`:

- Add keyframes for object transforms and material intensity/visibility.
- Provide interpolation helpers for alignment phases.

`cameras.py`:

- Create and name the wide camera.
- Create and name the card close-up camera.
- Configure focal lengths, clipping, depth of field, and timeline markers for
  camera switching if used later.

## Data Flow

The scene script defines the simulation parameters and timeline phases. It then
calls reusable helpers in this order:

1. Reset scene and configure render settings.
2. Create materials.
3. Build static geometry: table, card, aperture, mount, lens.
4. Build beam geometry and return-spot markers from the initial parameter set.
5. Add keyframes for lens tilt, lens decenter, reflected beams, and card spots.
6. Add wide and close-up cameras.
7. Save the generated scene only when an explicit output path is provided.

The generated Blender scene is the output. The Python source remains the source
of truth.

## Error Handling

The first implementation should fail early with clear messages when:

- It is not run from Blender and `bpy` is unavailable.
- Required Blender APIs are missing.
- A numeric scene parameter is nonsensical, such as a nonpositive aperture
  diameter or beam diameter.
- An optional save path points to a directory that does not exist.

Errors should be plain Python exceptions with actionable messages. The helper
modules should avoid silently swallowing Blender API failures.

## Testing And Verification

Because Blender may not be installed in every development environment, tests
should be split into two levels:

- Standard Python checks that can run without Blender for parameter validation,
  alignment math, and import-safe modules that do not require `bpy` at import
  time.
- Manual or optional Blender verification that runs the scene script inside
  Blender and confirms that the scene generates without errors.

Recommended verification for the first implementation:

```bash
uv run pytest
uv run ruff check simulations/blender
blender --background --python simulations/blender/scenes/achromat_back_reflection.py
```

If Blender is unavailable, document that limitation and still run the Python
checks that do not require Blender.

## Documentation

`simulations/blender/README.md` should explain:

- What the simulation directory contains.
- How to run the first scene in Blender.
- Which files are source-controlled outputs and which are generated artifacts.
- The intentional approximation boundary between teaching visualization and
  physical optical simulation.

The main Sphinx docs do not need to link the simulation in the first
implementation unless the generated script is stable and easy to run.

## References

- Blender Python API quickstart:
  https://docs.blender.org/api/current/info_quickstart.html
- Thorlabs AC254-100-A-ML product page:
  https://www.thorlabs.com/item/AC254-100-A-ML

