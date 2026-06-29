.. _optical_alignment_walking_beam:

#################################
Walking A Beam Through Two Irises
#################################

Goal
====

The goal is to make a laser beam pass through the centers of two same-height
irises after two steering mirrors. The first iris defines the near point on the
desired optical axis. The second iris defines the far point. When the beam is
centered on both irises, the beam position and angle match the line selected by
those two apertures.

This is a geometric alignment method. It does not require the downstream optic
to be installed yet, which makes it useful when setting beam height, preparing a
beam expander path, or establishing a clean reference line across an optical
table.

.. card:: Walking-Beam Alignment Simulation

   This simulation shows a Z-fold made from two kinematic mirror mounts and two
   same-height irises on a 25.4 mm table-hole row. The wide view shows the two
   mirrors walking the beam onto the iris row. The close-up view shows the near
   and far iris readouts during each correction.

   .. raw:: html

      <video controls preload="metadata" style="width:100%;">
        <source src="../_static/optical_alignment/videos/walking_beam_alignment_stacked.mp4" type="video/mp4">
        Your browser does not support embedded video.
      </video>

   `Download the walking-beam alignment movie <../_static/optical_alignment/videos/walking_beam_alignment_stacked.mp4>`_


Why This Works
==============

A straight beam is fully specified by two points. Two irises therefore define
the desired path: the beam must pass through the first aperture and then through
the second aperture without clipping.

The two mirrors provide two coupled controls. A first-mirror adjustment changes
where the beam lands at the near iris and also changes the downstream angle. A
second-mirror adjustment changes the downstream angle and therefore moves the
far iris spot strongly. Because the controls are coupled, a single pass is
rarely perfect. Alternating between the near iris and the far iris converges on
the line through both aperture centers.

Use small iris openings only after rough alignment is close. Starting with a
larger opening prevents accidental clipping and makes it easier to see which
mirror adjustment is moving the beam in the intended direction.


Step-By-Step Protocol
=====================

1. Set both irises to the same height and place them on the desired beam path.
   A table-hole row is a convenient reference for a straight horizontal path.

2. Open both irises enough that the rough beam can be found safely without
   clipping.

3. Place two steering mirrors before the first iris. A Z-fold is often
   convenient because the outgoing beam can travel straight down the iris row.

4. Roughly steer the beam so that it reaches the first iris and continues toward
   the second iris.

5. Adjust the first mirror to center the near iris. Watch the beam spot at
   Iris 1 and use small, deliberate mirror motions.

6. Adjust the second mirror to center the far iris. Watch the beam spot at
   Iris 2 and bring it to the same-height aperture center.

7. Return to the first mirror and re-center Iris 1. The second-mirror change
   usually perturbs the near iris slightly.

8. Return to the second mirror and re-center Iris 2.

9. Iterate until both iris spots stay centered after each correction.

10. Reduce the iris openings and repeat the final corrections. Stop when the
    beam passes cleanly through both apertures at the working aperture size.


Troubleshooting
===============

If Iris 1 centers but Iris 2 moves far away, the mirror corrections are too
large or the initial Z-fold geometry is too coarse. Open the far iris, make a
rough second-mirror correction, and then restart with smaller movements.

If Iris 2 centers but Iris 1 no longer transmits, return to the first mirror.
This is the normal coupling between the two controls, not a sign that the
method failed.

If the beam clips both irises at different heights, recheck the mechanical
height of the iris centers before continuing. Walking the beam cannot fix a
reference line defined by apertures at different heights.

If the beam shape changes or becomes crescent-shaped at an iris, the beam is
clipping. Open the iris, recover a full round spot, and only then close the
aperture again.
