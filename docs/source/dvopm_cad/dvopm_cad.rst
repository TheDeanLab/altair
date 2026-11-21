.. _dvopmcad-home:

############################
CAD Files and Machined Parts
############################

This page identifies the custom Altair-dvOPM parts that must be machined and distinguishes them from the vendor models and assembly dependencies included in the complete CAD package. It is intended as a manufacturing handoff and pre-assembly checklist; the engineering bill of materials remains in :doc:`../dvopm_baseplate_design/dvopm_baseplate_design`.

CAD Packages
____________

The `complete CAD assembly and dependency folder <https://github.com/TheDeanLab/altair/tree/main/downloads/dvOPM/CAD/Final%20Assembly%20and%20Dependent%20Files>`_ contains the Autodesk Inventor system assembly, subsystem assemblies, custom components, vendor models, project files, and their dependencies. Download the repository to preserve the folder structure required to open the complete system assembly and inspect component relationships.

The complete assembly folder is **not** a machining list. It contains many commercial components that should be purchased rather than manufactured. Only the STEP files listed below from ``Final Machined Parts`` are designated for machining.

Manufacturing Notes
___________________

- Machine each listed STEP file in the stated quantity.
- When a PDF drawing is provided, send both the STEP model and drawing to the machine shop. The drawing contains thread callouts that may not be communicated completely by the STEP geometry.
- We machined the custom components from 6061-T6x aluminum with a general machining tolerance of :math:`\pm0.005` inches and recommend the same specification for reproduction. Any dimensions or thread callouts stated explicitly in a supplied drawing take precedence.
- Confirm that the STEP file and drawing describe the same revision before ordering. Do not substitute similarly named files from the older ``To Machine`` folder.
- Quantities marked as configuration-dependent should be confirmed against the selected Powell-lens mounting configuration before release.

Detection Module
________________

.. list-table:: Detection-module machined parts
   :header-rows: 1
   :widths: 23 8 39 30

   * - Part
     - Qty
     - Purpose
     - Manufacturing files
   * - Detection Baseplate
     - 1
     - L-shaped structural baseplate that registers the filter wheel, KCB2 fold-mirror mount, camera-positioning stages, and detection-module LS-50 mounting interface.
     - :download:`STEP <../../../downloads/dvOPM/CAD/Final Machined Parts/Detection Baseplate.stp>`; :download:`threaded-part drawing <../../../downloads/dvOPM/CAD/Final Machined Parts/Detection Baseplate.pdf>`
   * - 38 mm to SM2 Adapter
     - 1
     - Couples the O1-side C60-FW/filter-wheel interface to the SM2 adapter stack.
     - :download:`STEP <../../../downloads/dvOPM/CAD/Final Machined Parts/38mm to SM2 Adapter.stp>`; :download:`threaded-part drawing <../../../downloads/dvOPM/CAD/Final Machined Parts/38mm to SM2 Adapter.pdf>`
   * - Camera Holder
     - 1
     - Secures the Ximea MU196MR-ON camera to the RP005 rotation stage above the MT1B focus stage.
     - :download:`STEP <../../../downloads/dvOPM/CAD/Final Machined Parts/Camera Holder.stp>`
   * - Camera Cap
     - 1
     - Replaces the factory camera cap after sensor-cover-glass removal and preserves clearance when the camera is rotated.
     - :download:`STEP <../../../downloads/dvOPM/CAD/Final Machined Parts/Camera Cap.stp>`; :download:`threaded-part drawing <../../../downloads/dvOPM/CAD/Final Machined Parts/Camera Cap.pdf>`

Illumination Module
___________________

Two functional side-plate variants are provided. The standard side plate places the D-shaped launch mirror at the nominal position used in the assembly. The second plate is 1.5 cm shorter, which leaves a slightly greater propagation distance from the point where the beam leaves the D-shaped mirror to the illumination focal plane. Because the launched beam is oblique, the focal plane is correspondingly farther from the mirror termination in both the vertical and lateral directions. Either variant can be used, and the user can select or adapt the plate according to the required focal-plane position and mechanical clearance.

.. list-table:: Illumination-module machined parts
   :header-rows: 1
   :widths: 23 8 39 30

   * - Part
     - Qty
     - Purpose
     - Manufacturing files
   * - Illumination Baseplate
     - 1
     - Main registered baseplate for the folded illumination relay, Powell-lens positioning assembly, slit, and final upward-fold assembly.
     - :download:`STEP <../../../downloads/dvOPM/CAD/Final Machined Parts/Illumination Baseplate.stp>`; :download:`threaded-part drawing <../../../downloads/dvOPM/CAD/Final Machined Parts/Illumination Baseplate.pdf>`
   * - Side Plate
     - 1
     - Standard side-plate variant that carries the D-shaped launch mirror at the nominal assembly position and establishes the final oblique illumination geometry.
     - :download:`STEP <../../../downloads/dvOPM/CAD/Final Machined Parts/Side Plate.stp>`
   * - Side Plate, 1.5 cm Shorter
     - 1
     - Shortened functional variant that places the illumination focal plane slightly farther from the mirror termination in both height and lateral position. Only the selected side plate is installed in the assembled microscope.
     - :download:`STEP <../../../downloads/dvOPM/CAD/Final Machined Parts/Side plate 1.5cm Shorter.stp>`
   * - Galvo Holder to Polaris Mount
     - 1
     - Holds the resonant galvo and provides its registered connection to the Polaris mounting stack.
     - :download:`STEP <../../../downloads/dvOPM/CAD/Final Machined Parts/GalvoHoldertoPolarisMount.stp>`; :download:`threaded-part drawing <../../../downloads/dvOPM/CAD/Final Machined Parts/GalvoHoldertoPolarisMount 3-8.pdf>`
   * - Mount for Slit VA100CP
     - 1
     - Connects the VA100CP mechanical slit to its registered Polaris post.
     - :download:`STEP <../../../downloads/dvOPM/CAD/Final Machined Parts/Mount for Slit VA100CP.stp>`
   * - M145-to-K1S4 Polaris Post Height Adjustment, approximately 0.75 inch
     - 2
     - Provides the custom 0.75-inch height offset used by the registered K1S4 mirror-mount stacks.
     - :download:`STEP <../../../downloads/dvOPM/CAD/Final Machined Parts/M145toK1S4PolarisPost_HeightAdjustment_approx_0p75inch.stp>`
   * - Polaris Post Height Adjustment, 0.25 inch
     - 2
     - Provides the custom 0.25-inch height offset used by the registered K1S4 mirror-mount stacks.
     - :download:`STEP <../../../downloads/dvOPM/CAD/Final Machined Parts/PolarisPost_HeightAdjustment_0p25inch.stp>`
   * - K1XY Polaris Post Height Adjustment, 0.5 inch
     - 1
     - Establishes the required height of the K1XY fiber-collimator mounting stack.
     - :download:`STEP <../../../downloads/dvOPM/CAD/Final Machined Parts/K1XYPolarisPost_HeightAdjustment_0p5in.stp>`
   * - LNR25M-to-Polaris Adapter
     - 1
     - Registers the Polaris post carrying the POLARIS-1XY/Powell-lens assembly to the LNR25M translation stage in Powell configuration 1.
     - :download:`STEP <../../../downloads/dvOPM/CAD/Final Machined Parts/LNR25MtoPolarisAdapter.stp>`
   * - Polaris Post-to-1XY Height Adjustment, approximately 0.5 inch
     - 1, configuration-dependent
     - Height adapter for a Polaris-post/POLARIS-1XY mounting stack. Confirm whether this part is required by the selected Powell-lens stage configuration before ordering.
     - :download:`STEP <../../../downloads/dvOPM/CAD/Final Machined Parts/PolarisPostto1XY_HeightAdjustment_approx0p5inch.stp.stp>`

Sample Holder
_____________

The sample holder is supplied as a two-part assembly. Machine one matching base-and-cover pair for each holder required by the laboratory.

.. list-table:: Sample-holder machined parts
   :header-rows: 1
   :widths: 23 8 39 30

   * - Part
     - Qty
     - Purpose
     - Manufacturing files
   * - Sample Holder Base
     - 1 per holder
     - Lower body of the sample-holder assembly; provides the stage interface and central specimen-access opening.
     - :download:`STEP <../../../downloads/dvOPM/CAD/Final Machined Parts/Sample Holder Base.stp>`; :download:`threaded-part drawing <../../../downloads/dvOPM/CAD/Final Machined Parts/Sample Holder Base.pdf>`
   * - Sample Holder Cover Top
     - 1 per holder
     - Matching upper retainer for the sample-holder base.
     - :download:`STEP <../../../downloads/dvOPM/CAD/Final Machined Parts/Sample Holder Cover Top.stp>`

Package Check Before Machining
______________________________

.. note::

   The manufacturing folder includes two functional illumination side-plate alternatives: the standard side plate and a version shortened by 1.5 cm. Only one side plate is installed in the microscope. Machine both supplied STEP files as listed, then select or adapt the variant that provides the required focal-plane position and clearance for the final assembly.

The following items should be confirmed before requesting a quotation:

- The side-plate variant selected for the final assembly has been identified.
- The selected Powell-lens configuration and its required adapters have been identified.
- The desired number of sample-holder base-and-cover pairs has been specified.
- Each threaded part is accompanied by its matching PDF drawing.
- The machine shop receives files only from the current ``Final Machined Parts`` folder.
