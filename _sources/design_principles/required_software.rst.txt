
.. _software-home:

########
Software
########

The **software for optical simulations and computer-aided design (CAD)** is optional and only required for users who wish to **modify or customize Altair**. However, **navigate is mandatory** for microscope operation unless an alternative **open-source acquisition platform** is used. For **Altair-LSFM**, which operates in a **sample-scanning geometry**, **shearing** is necessary to properly align data spatially; while various software options exist, we provide **Python-based scripts** for this task. Lastly, **deconvolution is optional**, depending on the user’s specific imaging and analysis needs.

.. _optical-simulation-software:

---------------

Optical Simulations
====================

Performing accurate optical simulations is essential for designing and validating the illumination pathway of
**Altair**. To facilitate this process, we used **Zemax OpticStudio (Ansys)** to model the full illumination
system, optimizing the placement of each optical element to achieve the desired focusing and collimation properties.

To replicate or modify these simulations, a **Zemax OpticStudio (Ansys)** professional or academic license is needed.
This enables optical modeling, ray tracing, and tolerance analysis. The **Zemax simulation files** used to design the
Altair illumination system are included in the project’s GitHub repository. These files allow users to inspect and
modify the optical layout, test different lens configurations, and refine performance metrics as needed.

---------------

.. _3d-design:

Computer-Aided Design
=====================

For the design of custom parts and the baseplate, we used **Autodesk Inventor**. Academic licenses for Autodesk
products are available free of charge on their `website <https://www.autodesk.com/education/edu-software/overview?sorting=featured&filters=individual>`_.

To ensure **Autodesk Inventor** correctly locates and manages the CAD files, it is necessary to set up a **new project**
and define the workspace. We recommend following these steps:

Setting Up a New Project in Autodesk Inventor
----------------------------------------------

1. **Launch Autodesk Inventor**
2. Navigate to **File → Manage → Projects**

   .. image:: Images/cad1.png
      :align: center
      :width: 60%

3. When the **Projects** window appears, select **New**

   .. image:: Images/cad2.png
      :align: center
      :width: 60%

4. Choose **New Single User Project**

   .. image:: Images/cad3.png
      :align: center
      :width: 50%

5. **Specify a Project Name** and set the **root directory of the cloned Altair GitHub repository** as the **Project (Workspace) Folder**

   .. image:: Images/cad4.png
      :align: center
      :width: 60%

By configuring Autodesk Inventor in this way, all CAD files associated with **Altair** will be properly linked,
ensuring seamless loading of all components and assemblies.

---------------

.. _microscope-control-software:

Microscope Control Software: navigate
=====================================

To control and operate **Altair**, we use **navigate**, a Python-based software package designed to provide
flexible and intelligent microscope control. **navigate** enables users to interact with the system through
a variety of advanced modalities, including **smart acquisition routines** that dynamically adjust microscope
performance based on the biological specimen.

Features of navigate
--------------------

**navigate** provides key functionalities that enhance the efficiency and adaptability of the Altair system:

- **Automated Smart Acquisition** – Dynamically optimizes imaging parameters in real time, adapting to specimen
  properties to improve image quality.
- **Hardware Abstraction Layer** – Enables seamless control of multiple hardware components, allowing users
  to configure, modify, and expand the microscope's functionality.
- **High-Throughput Data Acquisition** – Facilitates volumetric imaging with high-speed acquisition routines,
  ensuring efficient data collection without compromising spatial or temporal resolution.

Installation and Access
-----------------------

**navigate** is **open-source** and publicly available on GitHub. Installation instructions, along with
comprehensive documentation, can be found here:
`navigate Installation Guide <https://thedeanlab.github.io/navigate/01_getting_started/02_software_installation/02_software_installation.html>`_

---------------

Post-Processing
===============

After image acquisition, post-processing is often necessary to extract meaningful biological information.
The **navigate** software package includes libraries for performing **basic image post-processing tasks**,
such as **shearing correction**, which can be applied directly to acquired datasets. We provide Python-based scripts in the
`post_processing` folder of this repository as an example.

Deconvolution
-------------

For more advanced processing, such as **deconvolution**, we recommend using **PetaKit5D**. This software
package is optimized for handling large-scale volumetric datasets and provides state-of-the-art deconvolution
algorithms to enhance image quality and resolution [#]_. **PetaKit5D** must be installed separately and can be found
here: `PetaKit5D GitHub Repository <https://github.com/abcucberkeley/PetaKit5D>`_

.. rubric:: Citations

.. [#] Ruan X, Mueller M, Liu G, Görlitz F, Fu TM, Milkie DE, Lillvis JL, Kuhn A, Gan Chong J, Hong JL,
   Herr CYA, Hercule W, Nienhaus M, Killilea AN, Betzig E, Upadhyayula S. *Image processing tools for
   petabyte-scale light sheet microscopy data.* **Nat Methods.** 2024 Dec;21(12):2342-2352.
   doi: `10.1038/s41592-024-02475-4 <https://doi.org/10.1038/s41592-024-02475-4>`_.
   PMID: `39420143 <https://pubmed.ncbi.nlm.nih.gov/39420143/>`_, PMCID: PMC11621031.

