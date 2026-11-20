# Achromat Fidelity Upgrade Design

## Goal

Increase the first Blender optics alignment simulation from a coarse teaching
approximation to a more physically plausible geometric visualization. The
scene should show an AC254-100-A-style cemented achromatic doublet in an
LMR1-style fixed mount, compute return spots from reflected ray bundles, show
different apparent reflection diameters, and render with shadows.

## Source Hierarchy

Use source data in this order:

1. Official Thorlabs AC254-100-A-ML mounted drawing for mounted lens and coating
   dimensions:
   `https://media.thorlabs.com/globalassets/items/a/ac/ac2/ac254-100-a-ml/20592-e0w.pdf?v=0116101917`
2. Official Thorlabs LMR1/M drawing for fixed mount dimensions:
   `https://thin01mstroc282prod.dxcloud.episerver.net/globalassets/items/l/lm/lmr/lmr1_m/0002-e0w.pdf?v=2026-01-16-12-52-35`
3. AC-series prescription values for the unmounted AC254-100-A optical surfaces
   when needed for ray tracing and mesh generation. Record these as prescription
   values, not manufacturing authority.

## Optical Model

The upgraded model uses an explicit prescription object for an AC254-100-A-like
doublet:

- lens diameter: 25.4 mm
- clear aperture: 90% of lens diameter
- effective focal length: about 100 mm
- back focal length: about 97 mm
- surfaces:
  - front convex spherical surface, N-BK7 side
  - cemented internal spherical interface between N-BK7 and SF5
  - weakly curved rear SF5 surface, visually close to flat
- center thicknesses:
  - first element: 4.0 mm
  - second element: 2.5 mm

The visual mesh should use the prescription surfaces directly enough that the
profile reads as a cemented doublet, while remaining robust and lightweight for
Blender rendering.

## Ray Model

The model traces a narrow collimated bundle from the card aperture to selected
reflective surfaces. For each surface, it:

- intersects each ray with the spherical surface;
- computes the local surface normal;
- reflects the incoming ray about that normal;
- intersects the reflected ray with the business-card plane;
- returns a spot center and diameter from the reflected bundle footprint.

The scene should use the most visually useful two reflections for the teaching
goal, while keeping the ray helper capable of handling additional surfaces.
The returned spots should generally have different diameters because different
surface curvature and effective reflection plane positions change the returned
bundle footprint.

## Scene And Rendering

Replace the cylinder lens with two transparent bonded glass elements and a
visible internal interface. Replace the torus mount with an LMR1-style fixed
mount: rectangular black-anodized body, central bore, retaining ring, spanner
slots, mounting base/post features, and clear aperture. Enable Blender shadows
with area lighting so the mount, card, and optical table feel grounded.

The existing render script remains the user-facing path. The fidelity upgrade
must preserve the wide, card close-up, and stacked movie outputs.

## Testing

Add non-Blender tests for:

- prescription constants and derived clear aperture;
- spherical sag and surface-normal behavior;
- ray bundle reflection returning centered spots when aligned;
- tilt/decenter producing surface-dependent offsets and different spot
  diameters;
- import-safe scene defaults including the AC254/LMR1 source labels.

Keep Blender-specific behavior verified by a short background smoke render.
