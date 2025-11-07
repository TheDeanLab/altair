
.. _altair-home:

#####################
**Altair**
#####################

Biologists are increasingly transitioning towards more complex assays that require volumetric imaging with high spatiotemporal resolution. Whether it is a developing embryo, the formation of an immunological synapse, cancer migrating through a 3D collagen matrix, these biological processes can only be understood when non-invasively and quantitatively evaluated in their entirety through time.

To meet these growing demands, we aim to develop simplified optical systems that provide cutting-edge imaging performance while ensuring ease of assembly and accessibility. By leveraging precision-engineered, baseplate-mounted designs, we eliminate unnecessary degrees of freedom, making high-resolution light-sheet microscopy more robust, reproducible, and approachable for researchers across disciplines. Our goal is to create powerful yet modular imaging platforms that enable biologists to focus on discovery rather than instrument complexity, accelerating the adoption of advanced volumetric imaging techniques.

-----------

**Project Philosophy**
=========================

- **High-performance, easy-to-assemble light-sheet microscopes** designed for broad accessibility.
- **Seamless integration** with **navigate** software for optimized operation and intelligent imaging workflows.
- **Precision-engineered optomechanical design** for ease of use, reproducibility, and low maintenance.
- **Streamlined optoelectronics and control architecture** for robust, reliable, and modular system operation.
- **Modular, adaptable platforms** that support future advancements in light-sheet microscopy.

--------

.. warning::

    Please be advised that while the Dean Lab has implemented several safeguards,
    there are inherent risks associated with the use of such
    mechanical and optical systems. Despite these precautions, the complexity and nature of
    hardware can lead to unpredictable outcomes. Therefore, the Dean Lab and UT
    Southwestern expressly disclaim any responsibility for any damages, losses, or
    injuries that may arise from or be related to the use of **Altair**.
    Users should be aware of these risks and agree to utilize **Altair** at their own risk.

.. warning::

    **Licensing Note:** These design materials are freely available to academic and non-profit users for research and educational purposes. Commercial or for-profit entities must obtain a license before use; please contact the `Office of Technology Development <https://www.utsouthwestern.edu/about-us/administrative-offices/technology-development/>`_ for more information.

--------

.. toctree::
   :caption: Table of Contents
   :maxdepth: 2

   introduction/introduction
   introduction/background
   design_principles/required_software
   future/index

.. toctree::
   :caption: Altair-SPIM v1
   :maxdepth: 2

   hardware/index.rst
   design_principles/design_process
   physical_assembly/physical_assembly
   system_characterization/system_characterization
   imaging/imaging
   live_cell/live_cell


.. toctree::
   :caption: Altair-ASLM/CTASLM/SPIM v1
   :maxdepth: 2

   baseplate2/baseplate2




**Authors**
============
Dr. John Haug performed all simulations, design, testing, and validation of Altair. Seweryn Gałecki provided
cells for testing imaging performance and assisted in their visualization. Dr. Kevin Dean oversaw and provided feedback on all research operations. This project also benefited from valuable feedback from the **Dean, Fiolka, and Danuser labs** at **UTSW**.

**Acknowledgements**
====================
The authors extend their gratitude to Calvin Jones and `Dr. Sophia Theodossiou <https://www.boisestate.edu/coen-mbe/directory/sophia-theodossiou/>`_ (Boise State University) for
their assistance in designing and printing the custom sample chamber, as well as **Melissa Glidewell** for her
initial evaluation of optical tolerances.


**Funding**
============
**navigate** is supported by the
`UT Southwestern and University of North Carolina Center for Cell Signaling
<https://cellularsignaltransduction.org>`_, a Biomedical Technology Development and Dissemination (BTDD) Center funded by the NIH National Institute of General Medical Science (RM1GM145399), and the `Center for Metastatic Tumor Imaging <https://www.metastasis-imaging.org>`_ program, a Cellular Cancer Biology Imaging Research (CCBIR) program funded by the NIH National Cancer Institute (U54CA268072).
