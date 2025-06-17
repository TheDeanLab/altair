.. _livecellimaging-home:

###############
Live-Cell Imaging
###############

Sample Chamber Design
^^^^^^^^^^^^^^^^^^^^^^

In addition to fixed-cell imaging, there are also a variety of live-cell imaging applications where observing the
evolution or behavior of a cell over time can be valuable. To be able to perform live-cell imaging, the most
important aspect that needs to be addressed compared to fixed-cell imaging is that of a heat-regulated
environment for the cells. In live-cell imaging, the typical temperature ranges that one would use are between
25-37C, with 90% of applications being done at 37C. We've traditionally done this temperature regulation in the past
using a combined system comprised of thermocouples (for detection the ambient temperature), heating pads (to heat the
cell sample chamber), and a heating controller (to manage signals to and from the thermocouples and heating pads and
ensure the chamber remains at a specific temperature). It's also important to note that in addition to the sample
chamber, gently heating the microscope objectives used is also advised to reduce potential effects of thermal
drifting that effect imaging performance.

Our live-cell imaging chamber is meant to serve as an upgrade to our pre-existing sample chamber design and provide
an all-in-one way to accurately heat the sample chamber as well as the two objectives used. The chamber
is designed for the Thorlabs TL20X-MPL illumination objective and Nikon N25X-APO-MP detection objective pairing. As
with our traditional chamber, there are two ports for these objectives with sets of o-ring grooves within them to
form a water-tight seal around the objectives themselves.

In comparison to our traditional chamber design, there are a few changes made in this variant. The first is that
there is not an additional third port for imaging of the light sheet itself. This allows us to place a heating pad
along the two sides of the chamber with no ports and increase the overall surface area that is actively heated on the
chamber. The other large change is that of additional large hoods around each of the objective ports. These hoods are
designed for heating pads to be able to be wrapped around them to apply indirect air heating to the objectives.


.. figure:: Images/thermocoupleassembly.png
    :align: center
    :alt: Live-Cell Sample Chamber

    **Figure 1** Our custom live-cell sample chamber


-------------

Parts List
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Similarly to our philosophy when trying to source all of our components in our system from as few distinct vendors as
possible, we sourced all of the heating elements for this system directly from Mcmaster Carr. There are ceratinly
other options one can go with to accomplish similar heating capabilities, but we'll be basing our full heating
assembly based on the following components:

.. collapse:: Live-Cell Heating Equipment

    .. list-table::
       :header-rows: 1

       * - **Part**
         - **Vendor**
         - **Purpose**
       * - Live-Cell Sample Chamber
         - Xometry
         - Custom-designed live-cell sample chamber
       * - Benchtop Autotuning Temperature Controller, Type J Thermocouple, 1 Bay
         - Mcmaster Carr (Tempco)
         - 1 Bay Temperature Controller for the larger heating pad on the sample chamber side
       * - Benchtop Autotuning Temperature Controller, Type J Thermocouple, 2 Bay
         - Mcmaster Carr (Tempco)
         - 2 Bay Temperature Controller for the heating pads associated with the microscope objectives
       * - 3" Dual Thermocouple Type J, 1/8" Diameter Probe
         - Mcmaster Carr (Reotemp)
         - Optional Dual-Probe Thermocouple for controlling objective temperatures
       * - 1" Threaded Thermocouple 1/4"-20 Threading
         - Mcmaster Carr
         - Threaded Thermocouples to screw into sample chamber, 3 total if not using Dual-Probe thermocouple
       * - 2x5" Adhesive Backed Heat Sheet
         - Mcmaster Carr (Benchmark Thermal)
         - Large heating pad to be placed on the outer surfaces of the sample chamber without objective ports
       * - 5x1" Ultrathin Heat Sheet
         - Mcmaster Carr (All flex solutions)
         - Heating pad to wrap around illumination objective port
       * - 6x1" Adhesive Backed Heat Sheet
         - Mcmaster Carr (Benchmark Thermal)
         - Heating pad to wrap around detection objective port


-------------

Live-Cell Imaging Full Assembly
______________________

Thermocouple Adapter Assembly
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Thermocouples often come without the neccessary adapter placed on the end of their wiring to connect them to a
temperature controller. Below in Figure 2 we show the general process to attaching one of these adapters to the two
thermocouple wires:

    1. Unscrew the screws on the outer shell of the adapter.
    2. Remove the outer shell element of the adapter.
    3. Unscrew the inner screws over both terminals of the adapter enough such that the metal plates can be lifted (4).
    5. Place the ends of the thermocouple wires beneath the metal plates of each terminal (red = -, white = +).
    6. Screw the inner terminal screws tight.
    7. Place the outer shell element back on the adapter and screw both screws into place on it.


.. figure:: Images/thermocoupleassembly.png
    :align: center
    :alt: Thermocouple Assembly

    **Figure 2:** Thermocouple adapter assembly process

-------------

Heater Adapter Assembly
^^^^^^^^^^^^^^^^^^^^^


.. figure:: Images/thermocoupleassembly.png
    :align: center
    :alt: Heater Adapter Assembly

    **Figure 3:** Heater adapter assembly process

-------------

Placing O-rings in the Sample Chamber
^^^^^^^^^^^^^^^^^^^^^

-------------

Placement of the Heating Pads on the Sample Chamber
^^^^^^^^^^^^^^^^^^^^^

-------------

Temperature Controller Assembly
^^^^^^^^^^^^^^^^^^^^^

-------------

Temperature Controller Settings
^^^^^^^^^^^^^^^^^^^^^

