.. _design-home:

##############
Design Process
##############

Initial Lens Selection
______________________

Prior to starting optical simulations in Zemax, it's convenient to start with straightforward
calculations to determine which lenses to use in the optical train to achieve the desired field of view (FOV) for your
detection path. In our case, our detection path consisted of a 400 mm tube lens and a Nikon 25x/1.1 numerical aperture (NA) immersion detection objective.

.. figure:: Images/DetectionPath.png
   :alt: Schematic of a standard, widefield detection path.
   :align: center
   :width: 100px

   **Figure 1:** A simple schematic for a widefield detection path. Here, a detection objective captures light, which is then focused onto the active sensor of a CMOS camera using a tube lens.

.. sidebar:: **Calculating the Focal Length of an Objective**
   :class: sidebar-note

   The focal length (:math:`f`) of a microscope objective can be determined using the **nominal focal length** of
   the manufacturer's standard tube lens and the **objective’s magnification**:

   .. math::

      f = \frac{f_{\text{tube lens}}}{M}

   where:

   - :math:`f_{\text{tube lens}}` is the standard focal length of the tube lens.
   - :math:`M` is the nominal magnification of the objective.

   Standard tube lens focal lengths vary by manufacturer:

   - **Nikon / Zeiss**: 200 mm
   - **Olympus**: 180 mm

   **Example Calculation**
   For a **Nikon 25× NA 1.1 objective**, the focal length is calculated as:

   .. math::

      f = \frac{200 \text{ mm}}{25} = 8 \text{ mm}



To determine the target FOV, start by determining the final magnification (M) of the system using the ratio of the focal lengths of the tube lens (:math:`f_{\text{TL}}`) and the detection objective (:math:`f_{\text{DO}}`, Equation 1).

.. math::

   M = \frac{f_{\text{TL}}}{f_{\text{DO}}}



From there, determine the resulting FOV of the detection path by dividing the total camera sensor size (in mm) by the magnification, and then converting into microns (Equation 2).

.. math::

   \text{FOV} \ (\mu m) = \left( \frac{W_{\text{Sensor}}}{M} \right) \times 1000

For our system, where :math:`f_{\text{TL}}` = 400 mm, :math:`f_{\text{DO}}` = 8 mm, and :math:`W_{\text{Sensor}}` = 13 mm,
this resulted in a FOV of ~266 :math:`\mu m`, meaning that we want to select lenses in our illumination path
to produce a light sheet as close to 266 :math:`\mu m` in length as we can achieve.

The overarching goal of a standard optical system is to both mold light into a particular shape and direct it to a
particular location. In our case, our optical system works to convert an input Gaussian beam into a thin light sheet that illuminates our sample. There are a few sets of criteria that help guide our potential lens selection:

    * As mentioned, we want our final light sheet size to ideally cover the full FOV of our detection path (~266 μm)
    * At the focus of our cylindrical lens, we want the beam spot size to stay under the size of our resonant galvo (12 mm diameter)
    * We need the focal distance between the cylindrical lens and the galvo mirror system to be greater than ~55 mm due to mechanical considerations of the mirror mount used

With these criteria in mind, we can calculate a theoretical estimate of what our beam size is after each of our lenses. We
do this by considering every pair of lenses (i.e. Lens 1 & 2, Lens 2 & 3, ...) as a sort of 4F magnification system,
where the resulting image size of the pairs is determined by the ratio of their focal lengths (:math:`f_n`) as follows:


.. figure:: Images/4FSystem.png
   :alt: A diagram of a 4f optical system.
   :align: center
   :width: 300px

   **Figure 2:** A diagram of a 4f optical system. Here, the ratio of the focal lengths of the lenses determines the magnification of the system.

Essentially, we can cascade these calculations through our lenses and make sure that our choices in their focal
lengths produce our desired beam characteristics as light propagates through the system. In our case,
our chosen system featured 4 lenses from Thorlabs:
`L1 = 30 mm <https://www.thorlabs.com/thorproduct.cfm?partnumber=AC254-030-A>`_,
`L2 = 80 mm <https://www.thorlabs.com/thorproduct.cfm?partnumber=AC254-080-A>`_,
`L3 (Cylindrical) = 75 mm <https://www.thorlabs.com/thorproduct.cfm?partnumber=ACY254-075-A>`_, and
`L4 = 250 mm <https://www.thorlabs.com/thorproduct.cfm?partnumber=AC254-250-A>`_.

We can then take these lens choices and load them into Zemax OpticStudio to verify the characteristics of our system.

.. figure:: Images/MonolithV1p1_CylindricalLensSchematic_V2.png
    :align: center
    :alt: Top and bottom views of an optical path.

    **Figure 3:** A schematic of the optical path for a light-sheet microscope. The system consists of four lenses, a cylindrical lens, a resonant galvo, a 45-degree mirror, and an illumination objective. Top and bottom views are shown.

----------------


Zemax Simulation Setup Process
______________________________

With our chosen lenses in mind, we can download Zemax files associated with each lens directly from the Thorlabs website
and set up our simulation.

.. figure:: Images/ThorlabsExample.png
    :align: center
    :alt: Thorlabs Zemax Download

    **Figure 4:** An example of a Zemax file download from Thorlabs. The file contains the optical properties of the lens, which can be imported into Zemax OpticStudio.

Here, we use Zemax as a tool to find the optimal placement of all the lenses in our system based on whether the input beam should be focused or collimated after each lens. As a general rule of thumb, one should build optical systems in Zemax in an element-by-element manner instead of adding all optical elements and then trying to optimize aspects of the full system at once. Our general flow involves adding a lens to the system and then optimizing for either a focused or collimated beam, followed by adding the next lens and repeating the process until all lenses are placed in the system. This is described in more detail below.

For our particular system, our generalized process went as follows:

    1. Create a new file that will be used as our lens assembly file
    2. Set aperture size in Zemax to match our original laser spot size (2.4 mm).
    3. Open the Zemax file associated with Lens 1, then copy and paste the surfaces into our assembly file.
    4. Use the optimization wizard to set a focusing optimization with the distance after L1 (f1) as the variable to find
       the correct position of L1's focus.

    .. figure:: Images/Spotwizard.png
        :align: center
        :alt: Optimization Wizard for Spot Size

    **Figure 5:** The optimization wizard in Zemax. Here, the user can set the optimization type and the variable to optimize. In this case, the user is optimizing for spot size.

    5. Run the optimization, then remove the variable for f1.
    6. Open the Zemax file associated with Lens 2, then copy and paste the surfaces into our assembly after Lens 1
    7. Use the Optimization Wizard to set an angular (collimation) optimization, with the distance between L1's focus and L2 (d1) as the variable.

    .. figure:: Images/Anglewizard.png
        :align: center
        :alt: Optimization Wizard for Collimation

    **Figure 6:** The optimization wizard in Zemax. Here, the user can set the optimization type and the variable to optimize. In this case, the user is optimizing for collimation.

    8. Optimize, then remove the variable for d1.
    9. Open the Zemax file associated with Lens 3, then copy and paste the surfaces into our assembly after Lens 2.
    10. Use the optimization wizard to set an *X*-focusing optimization with the distance after L3 (f3) as the  variable.
    11. Optimize, then remove the variable for f3.
    12. Place in resonant galvo and 45 degree mirror surfaces at the location of f3.
    13. Open the Zemax file associated with Lens 4, then copy and paste the surfaces into our assembly after the 45 degree mirror.
    14. Use the optimization wizard to set an *X*-collimation optimization with the distance between the 45 degree mirror and L4 (d3) as the variable.
    15. Optimize, then remove the variable for d3.
    16. Open the Zemax file associated with our Illumination Objective, then copy and paste the surfaces into our assembly  after L4.
    17. Use the Optimization Wizard to set an *X*-focusing Optimization with the distance between L4 and the objective (d4) as the variable.
    18. Optimize

----------------

Zemax Simulation Analysis
_________________________

Within Zemax, there are numerous analysis tools available to investigate different characteristics of optical systems. Our analysis is primarily guided by the Geometric Image Analysis, Huygens PSF, and Through Focus Spot tools. Zemax natively uses geometric ray tracing in most operations such as beam optimization. This is generally acceptable for most optical systems; however, as our output light-sheet size approaches the diffraction limit (:math:`\frac{\lambda}{2NA}`), we also need to consider diffraction effects in our analysis.

The Huygens PSF analysis tool is how we incorporate diffraction effects into our analysis; we anticipate results from this analysis to be more in line with what would be observed on the physical system. Based on the cross section of our Huygens PSF analysis, we can see that the expected full width at half maximum (FWHM) of the light sheet is around 0.376 :math:`\mu m`.

We compare the results of these two analyses for our optimized illumination path below, where we show the full XY profile
as well as cross-sections through the center row of both beam profiles. In this case, the FWHM of both analyses ends up
being quite similar at ~0.37 :math:`\mu m`.

.. figure:: Images/HuygensvsGeo.png
    :align: center
    :alt: Comparison of Geometric Image Analysis and Huygens PSF analysis for our optimized system

    **Figure 7:** A comparison of the Geometric Image Analysis and Huygens PSF analysis for our optimized system. The FWHM of the light sheet is expected to be around 0.376 :math:`\mu m`.

Through Focus Spot analysis allows us to essentially see the evolution of the light sheet through the point of focus, where we can then estimate a sort of range where we expect the width of the light sheet to be thin enough for our imaging purposes, where the maximum usable light sheet width is the FWHM at the focus multiplied by :math:`\sqrt{2}`. The optimized illumination path simulation files are available in the `Zemax <https://github.com/TheDeanLab/altair/tree/main/downloads/base/zemax>`_ folder of our repository.

----------------

Zemax Tolerance Analysis
________________________

When considering building physical systems using Zemax, an additional analysis tool known as tolerancing becomes increasingly important. No physical system is perfect, and tolerancing is essentially the process of understanding how sensitive different elements in a system are to various perturbations. This can be along the lines of how sensitive the collimation or magnification of a 4F system is to small physical displacements of the two lenses that comprise it. Similarly to Zemax's optimization process, tolerancing also utilizes a merit function. This merit function is fully customizable, and serves to define how well a particular system is performing. In the case of our system, we chose our merit function to factor in both the size and displacement of the output light sheet relative to the perfectly optimized instance. Our merit function used in Zemax is also shown below, where there are 4 operands that track the size and position of the beam in both x and y.

.. figure:: Images/ToleranceMF.png
    :align: center
    :alt: Tolerance Merit Function

    **Figure 8:** The merit function used in our Zemax tolerancing analysis. The merit function is used to evaluate the performance of the system based on the size and position of the output light sheet.

With a merit function criterion set, the next step is to designate which elements of the system will change and by how much. In our case, we wanted to associate our tolerance analysis with the machining tolerances given by fabrication companies. In general, looking across different companies, the standard machining tolerance is around +-0.005" and the finer machining tolerance is around +-0.002". For our analysis, we wanted to understand how angular deviations in elements due to machining tolerances in the alignment dowel pins would affect overall system performance. This is depicted below, where in the worst-case scenario of one pin being offset +0.005" and the other -0.005", the resulting angular offset would be around 1.45 degrees.

.. figure:: Images/AlignmentHole.png
    :align: center
    :alt: Angular offset of elements imparted by machining tolerances of dowel pin holes

    **Figure 9:** The angular offset of elements due to machining tolerances of alignment dowel pin holes. In the worst case scenario, the angular offset is around 1.45 degrees.

In addition to perturbations to a system, in tolerancing analysis a compensator can also be defined as a designated element that can be changed to mitigate the effects of other tweaked elements in the system. In our case, we define the XY position of our illumination objective as a compensator with a range of +-0.25 mm, which matches the XY translation adjustment associated with our `objective mount <https://www.thorlabs.com/thorproduct.cfm?partnumber=POLARIS-1XY>`_.

The basic way in which this analysis works is that Zemax performs a designated number of Monte Carlo simulations, each with a different perturbation made to the system, and evaluates the merit function for each of those systems. Based on the change to the merit function for each instance, tolerancing outputs a report that describes the sensitivity of the merit function to each element in the system. In some cases, tolerancing analysis provides information about how much a parameter can vary before performance becomes unacceptable. An example is a lens designer tolerancing the radii or material properties of a lens to ensure its focal length stays above or below a certain value. For our system, even with our designated merit function, it is difficult to directly ascribe a cutoff value of the merit function as acceptable, so we primarily use tolerancing analysis as a way to guide general trends of sensitivity in system elements.

This is shown below, where in this instance we can see that, in the case of our system, the element corresponding to the 24th surface (the galvo mirror) causes the most change to the merit function as it becomes perturbed. In all cases, the largest perturbations in the system (i.e. when the angular offset of an element is maximum at +-1.45 degrees) result in the largest changes to the merit function.

We also set our tolerance analysis to output the best and worst instances from the Monte Carlo simulations as individual files, and the corresponding geometric image analysis windows are shown for each as well as the nominal optimized case for comparison. It's clear that in the worst case scenario, it looks like the resulting light sheet is shorter in span than that of the nominal and best cases.

.. figure:: Images/Tolerance_Coarse.png
    :align: center
    :alt: Results of tolerancing analysis when the offset corresponded to +-0.005"

    **Figure 10:** Results of the tolerancing analysis when the offset corresponded to +-0.005". The merit function is used to evaluate the performance of the system based on the size and position of the output light sheet.

To understand how tighter tolerances might affect system performance, we set our angular offset to correspond to tighter machining tolerances offered online at +-0.002". Typically, tighter machining tolerances correspond to an increase in price, so understanding whether tighter tolerances would benefit a system is useful. We can run the same tolerance analysis as before, but this time with an angular offset of +-0.581 degrees, and show the results below. In this analysis, once again, the element that affects the system most adversely is the galvo mirror element. The deviations in the resulting merit functions from this element are about a tenth of that of the larger machining-tolerance case. Visually, in the worst-case example, one can see that the resulting light sheet looks much closer to the nominal case than before.

.. figure:: Images/Tolerance_Fine.png
    :align: center
    :alt: Results of tolerancing analysis when the offset corresponded to +-0.002"

    **Figure 11:** Results of the tolerancing analysis when the offset corresponded to +-0.002". The merit function is used to evaluate the performance of the system based on the size and position of the output light sheet.


The results of our tolerancing analysis, as well as the associated lens files for our best and worst-case instances for both fine and coarse tolerancing, are available `here <https://github.com/TheDeanLab/altair/tree/main/downloads/base/zemax>`_.

----------------

Baseplate Design
________________

When satisfied with the results of simulations, the optimized values in Zemax can then be used to design
our baseplate. This process involves taking the optimized distances between our various optical elements
and then considering how each of those elements are mounted in a physical system, as in Zemax all of the elements are effectively suspended in midair like below:

.. figure:: Images/CylindricalDesign6_30_90_75_250flip4.png
    :align: center
    :alt: Zemax Elements Floating

    **Figure 12:** A Zemax diagram of the elements in our system. Here, the elements are shown floating in midair.

For mounting our elements, we utilize the `Polaris <https://www.thorlabs.com/navigation.cfm?guide_id=2368>`_ line from Thorlabs, which are designed with long-term stability and alignment in mind. Each component is characterized in part by two dowel pin alignment holes to ensure subsequent mounted elements are aligned along a specific axis. In the baseplate design, we are essentially deciding on the location for the mounting holes of the Polaris posts we're using, which is not the same as the locations of the elements themselves from Zemax.

.. figure:: Images/PolarisScheme.png
    :align: center
    :alt: Polaris Scheme

    **Figure 13:** A schematic of the Polaris mounting system. The system is characterized by two dowel pin alignment holes to ensure subsequent mounted elements are aligned along a specific axis.

While we are able to use most of our element mounts from the Polaris line, for the cylindrical lens L3 we needed a mount capable of rotating the lens, which at this time is not something available from Thorlabs. In our case we designed an additional mounting element that allows the use of a basic Thorlabs
`RSP1 rotation mount <https://www.thorlabs.com/thorproduct.cfm?partnumber=RSP1>`_, but still ensures alignment with the other Polaris elements. The CAD file for this mount is available for download `in our CAD directory <https://github.com/TheDeanLab/altair/tree/main/downloads/base/cad>`_.

.. figure:: Images/RotationMount.png
    :align: center
    :alt: Rotation Mount Adapter
    :width: 30%

    **Figure 14:** A schematic of the rotation mount adapter. The adapter allows for the rotation of the cylindrical lens while ensuring alignment with the other Polaris elements.

With the method in which each of the elements needs to be mounted decided upon, we then went over the product schematics for each mount to understand the z-displacement that they impart upon the element mounted within them relative to where the Polaris post central mounting hole would need to be. This idea is depicted below, where when considering how to space two lenses from each other there is essentially three components to take into account:

    1. The distance between the lenses decided from simulation
    2. The thickness of the lenses themselves
    3. The distance between the center of the Polaris post and the start of the lens in the mount

.. figure:: Images/PostSpacingConsiderations.png
    :align: center
    :alt: Post Spacing Considerations
    :width: 50%

    **Figure 15:** A schematic of the considerations for spacing two lenses from each other. The distance between the lenses is decided from simulation, the thickness of the lenses themselves, and the distance between the center of the Polaris post and the start of the lens in the mount.


Once the locations of the mounting holes were determined, we used Autodesk Inventor to design the full baseplate. The baseplate is essentially just a mounting hole and the two dowel pin holes for every element, as well as four mounting holes for the baseplate itself. These four baseplate mounting holes were spaced in increments of inches such that the baseplate can either be screwed directly into an optical breadboard table or into additional posts that can keep the assembly at a desired height.

.. figure:: Images/Baseplate.png
    :align: center
    :alt: Baseplate

    **Figure 16:** A schematic of the baseplate. The baseplate is characterized by mounting holes for each element and four mounting holes for the baseplate itself.

With the baseplate designed, our final assembly for our illumination path looks as follows:

.. figure:: Images/BaseplateAssembly_Iso.png
    :align: center
    :alt: Baseplate Assembly Iso

    **Figure 17:** An isometric view of the baseplate assembly.

.. figure:: Images/BaseplateAssembly_Top.png
    :align: center
    :alt: Baseplate Assembly Top

    **Figure 18:** A top view of the baseplate assembly.

The CAD files for our baseplate design are available in the following `GitHub repository <https://github.com/TheDeanLab/altair/tree/main/downloads/base/cad>`_.

----------------

Physical Coordinate Definitions
_______________________________

It should be noted briefly that when discussing our physical microscope systems using navigate software, the coordinate-axis definitions are different from those in our simulations. This is due to differences between the standardized axis definitions used in our previous systems and how Zemax defines these same axes. This difference is depicted in the figure below:

.. figure:: Images/CoordinateSchemeChange.png
    :align: center
    :alt: Difference in coordinate axes for simulation and physical setup

    **Figure 19:** A schematic of the difference in coordinate axes for simulation and physical setup.
