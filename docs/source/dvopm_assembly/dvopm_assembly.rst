.. _dvopmassembly-home:

######################################
DV-OPM Baseplate Assembly & Alignment
######################################

Detection Train Assembly
________________________
The detection assembly consisted of a Mitakon Speedmaster 65 mm f/1.4 photographic lens acting as the primary objective (O1), followed by a filter wheel, a 90° folding mirror, a Nikon AF-S NIKKOR 85 mm f/1.4G lens serving as the secondary objective (O2), and a CMOS camera, the Ximea MU196MR, for image acquisition. In contrast to conventional oblique plane microscopy (OPM) systems employing an objective lens and tube lens, this configuration relies solely on 2 coupled photographic lenses with careful alignment. With the absence of tube lenses, the overall resolution of the system is limited by the pixel size of the detection camera; hence, the Ximea MU196MR was chosen due to having a 1.4-micron pixel size. All optical elements were precisely calculated, pre-aligned, and mounted onto a custom base plate, resulting in a mechanically constrained configuration that requires minimal alignment. 
Due to spatial and mechanical constraints of each optical elements as well as the non-telecentricity of the 2 photographic lenses, the relative spacing between the 2 was predetermined and optimized using simulation from Zemax to ensure optimal imaging performance.

The alignment is centered around the filter wheel, which serves as the primary optical reference. It start with setting up a reference beam for your baseplate.

Setting up reference beam steps:

    1. Place the laser source on an elevated platform above your baseplate to shine the laser beam downward to the baseplate.
    2. Generate a collimated beam from the source using a collimator. Here, we used a reflective collimator (Thorlabs RC08APC-P01) to achieve a desire beam diameter of 7.3 mm. 
    3. Direct the collimated beam downward using a 45 degrees angle mirror. In this case, we used a 1” right-angle kinematic mount (Thorlabs KCB1) to reflect the beam downward to the detection system. 
    4. Mount both the collimator and folding mirror on translation stages to allow fine positioning of the beam.  
    5. Install 2 irises along the propagation path. 
    6. Place a flat mirror on the optical table at the beam incidence point to check for back-reflection.. 
    7. In an iterative manner, adjust the tip and tilt of the 1” mirror and its rotation to ensure the back reflected beam travel back to the 2 irises.
    8. Once complete, this establishes a straight and stable reference beam for downstream alignment.

    .. figure:: Images/iris_tube.png
        :align: center
        :alt: Example of reference beam on with irises.
        :caption: Example of reference beam on with irises mounted on translation stages.

    .. figure:: Images/iris_check_alignment.png
        :align: center
        :alt: Check for beam symmetry at irises.
        :caption: Make sure the beam is center on the iris.

    .. figure:: Images/flat_mirror.png
        :align: center
        :caption: Installation of a flat mirror for back reflection.

    .. figure:: Images/iris_not_align.png
        :align: center
        :alt: example of not aligned beam

        :caption: Example of a misaligned beam.

        
The next step is to set up the photographic lens. Since these 2 lens are not telecentric, it’s important to set up these lenses correctly to ensure minimal aberration and optimal performance.  

O2 must be operated with its focus locked at infinity and its aperture fully open by rotating the focus ring of the camera Setting O2 to infinity focus immobilizes the internal focusing groups of the photographic lens, fixing the effective focal length and the locations of the entrance and exit pupils.

..  figure:: Images/o2_focus.png
    :align: center
    :alt: Image of O2 lock in focus.
    :caption: Lock the focus of O2 to infinity by rotating its focus adjustment.

Since this Nikon AF-S doesn’t has a mechanical aperture adjustment, we need to manually open its aperture. Fortunately, it can be done by inserting a firm plastic piece into the camera’s control (which can be found on the back pupil of the lens facing the sensor). Here, we use hard cardboard to fully open the aperture and to step up the camera.

.. figure:: Images/o2_aperture.png
    :align: center
    :alt: Example of stepping up O2
    :caption: Open O2's aperture with a cardboard piece.

The focus of O1 doesn’t affect the overall performance of the system so it can be ignored, but O1 has an aperture setting allowing you to step down the camera; hence adjusting its NA. The system can be optimized to utilize the full aperture (NA = 0.36 ) if necessary. Due to the non-telecentric and non-aberration-correction nature of the lens, as well as the filter wheel’s aperture of the current configuration being smaller than the back pupil of O1, operating at full NA will introduce significant astigmatism aberration to the system without improving your overall resolution.


Next, we set up the baseplate to put everything together.
    1. Install a 2” mirror into a 2” kinematic mount (Thorlabs KCB2) and the filter wheel into a predetermined position on the custom base plate. 
    2. Place a ground glass alignment, or a pinhole, at the entrance of the filter wheel. 
    3. Position your base plate such that the reference beam goes straight through your pinhole. You should see the light exit the baseplate. 
    4. Install a mirror in a 4” lens tube with a mirror mounted at the end and check for back reflection, and adjust the tip/tilt of the kinematic mirror to establish a straight beam path for the exit beam. 

.. figure:: Images/baseplate_mounting.png
    :align: center
    :alt: Example of mounted filterwheel and kinematic mount on the baseplate.
    :caption: Example of mounted filterwheel and kinematic mount on the baseplate.

.. figure:: Images/filter_entrance.png
    :align: center
    :alt: Image of the entrace of filterwheel
    :caption: Demonstration of center alignment by translating the reference beam.

.. figure:: Images/mirror_tubes.png
    :align: center
    :alt: Example of a mirror mount on a tube to check for back reflection.
    :caption: Example of a mirror mounted on a lens tube to check for alignment of the kinematic mount.

.. figure:: Images/misaligned_filter.png
    :align: center
    :alt: Example of misaligned mirror mount with back reflection.
    :caption: Example of a misaligned beam with back reflection by adjusting tip/tilt of the mirror.

.. figure:: Images/aligned_filter.png
    :align: center
    :alt: Example of aligned mirror.
    :caption: Example of an aligned beam with back reflection by adjusting tip/tilt of the mirror.


Once the system is established, install O2 in a reversed configuration and the camera in place to find the optimal focus position. Plug in and rotate the camera to roughly 45 degrees, where the entrance is parallel to O2. Shine a big laser beam down to O2 (ideally fill its back aperture) and translate the axial stage until the focus is nice and sharp on the camera using its software. Install some neutral density filter if necessary.

.. figure:: Images/o2_camera.png
    :align: center
    :alt: Demonstration set up to find the focus of the camera.
    :caption: Demonstration set up to find the focus on the camera.


Illumination Train Assembly
___________________________

Placeholder

