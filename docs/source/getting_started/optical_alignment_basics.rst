.. _optical_alignment_basics:

############################
Basics of Optical Alignment
############################

The goal is to make the optic normal to the incoming beam and centered on the
beam path. A simple aperture card lets you see light that reflects from the
optic and returns toward the source. When the useful back-reflection spots are
centered on the aperture, the optic is close to normal incidence and centered
well enough to continue the alignment.

This method is useful because it gives a fast, sensitive readout before moving
to more complicated system-specific alignment steps. It does not replace later
checks of beam height, beam walk, collimation, or image quality, but it helps
establish a clean starting condition for each optic.

.. card:: Achromat Back-Reflection Simulation

   This simulation shows a collimated 561 nm alignment beam passing through a
   small aperture in a card, reflecting from an achromatic doublet, and returning
   two spots to the card. The top view shows the physical layout. The lower view
   shows the aperture-card readout as tilt and position are corrected.

   .. raw:: html

      <video controls preload="metadata" style="width:100%;">
        <source src="../_static/baseplate2_alignment/alignment/videos/achromat_back_reflection_stacked.mp4" type="video/mp4">
        Your browser does not support embedded video.
      </video>

   `Download the alignment movie <../_static/baseplate2_alignment/alignment/videos/achromat_back_reflection_stacked.mp4>`_


Why This Works
==============

When a lens is placed in a laser beam, a small amount of light reflects from
each optical surface. For a simple lens or achromat, the most visible returns
often come from the front and rear surfaces. These returns appear as distinct
spots on the card.

Flat or nearly plano surfaces return a crisp, collimated spot that is roughly
the same diameter as the incoming alignment beam. Spherical or curved surfaces
can return spots that expand or focus, depending on the curvature of the surface
and the distance back to the card. In compound optics, the different surfaces
can therefore produce spots with different sizes.

The card gives those returns a visible target. The aperture marks the incident
beam position. If a return spot lands on the aperture, that reflected ray bundle
is traveling back along the incident beam path.


Setup
=====

Use a visible, low-power, collimated alignment beam. A 561 nm beam is convenient
when it is available, but the same geometry applies to other visible alignment
wavelengths. Keep the beam power low, use proper laser safety practices, and
avoid looking directly into any specular reflection.

Place a target card with a small aperture in the beam before the optic. A
business card with a narrow aperture works well because it blocks enough light
to reveal the return spots while still allowing the incident beam to pass. The
aperture must be centered on the true beam path before the optic is inserted.
If the aperture is not centered, the card itself biases the measurement.

Mount the optic downstream of the card. Keep enough space between the card and
optic for the return spots to separate visibly, but not so much space that weak
reflections become hard to see.


Interpreting The Reflection Spots
=================================

If the beam is not centered on the optic, the back reflections will be displaced
on the card. Lateral displacement of the optic moves the return spots laterally.
Vertical displacement also moves the return spots on the card because the card
records the beam position in its transverse plane.

When the beam is normal to the optic, the useful return spots should move in a
symmetrical way as the optic is centered. If the optic is tilted relative to the
laser propagation direction, the return spots will not be displaced
symmetrically. This asymmetry is the key sign that angle must be corrected
before position can be trusted.

The aperture card is part of the measurement. A shifted, tilted, damaged, or
poorly sized aperture can make a good optic alignment look bad, or make a bad
alignment look better than it is. Recheck the aperture position whenever the
beam path or card position changes.


Step-By-Step Protocol
=====================

1. Establish a clean, collimated alignment beam at the desired beam height.

2. Place the aperture card upstream of the optic location.

3. Center the aperture on the incident beam. The beam should pass cleanly
   through the aperture without clipping.

4. Insert the optic in its mount downstream of the card.

5. Observe the return spots on the card. For an achromat, expect more than one
   visible return, and expect the spots to have different diameters.

6. Correct angular alignment first. Adjust tip and tilt until the useful return
   spots move symmetrically toward the aperture.

7. Correct lateral and vertical position. Translate the optic until the useful
   return spots are centered on the aperture.

8. Iterate angle and position adjustments. These degrees of freedom are coupled,
   so one pass is rarely enough.

9. Confirm the alignment. Translate the card slightly along the beam path and
   confirm that the useful return spots remain consistent with a centered,
   normal optic.

10. Continue to the next optic or to the system-specific alignment step.


Complex Optics
==============

Objectives and other multi-element assemblies can produce many back reflections.
Do not try to center every faint ghost reflection. Instead, identify the
reflections that are meaningful for the alignment step and use those returns
consistently.

The general principle remains the same: when the optic is centered and normal
to the beam, the useful return spots should come back toward the aperture in a
predictable and symmetric way. The more complicated the optic, the more
important it is to document which reflections are being used as the alignment
reference.
