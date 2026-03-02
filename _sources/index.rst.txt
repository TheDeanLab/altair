
.. _altair-home:

#####################
**Altair**
#####################

`eLife Article 106910 <https://elifesciences.org/articles/106910>`_ | `DOI: 10.7554/eLife.106910 <https://doi.org/10.7554/eLife.106910>`_

Biologists are increasingly transitioning toward more complex assays that require volumetric imaging with high spatiotemporal resolution. Whether studying a developing embryo, the formation of an immunological synapse, or cancer cells migrating through a 3D collagen matrix, these biological processes can only be understood when non-invasively and quantitatively evaluated in their entirety over time.

To meet these growing demands, we aim to develop simplified optical systems that provide cutting-edge imaging performance while ensuring ease of assembly and accessibility. By leveraging precision-engineered, baseplate-mounted designs, we eliminate unnecessary degrees of freedom, making high-resolution light-sheet microscopy more robust, reproducible, and approachable for researchers across disciplines. Our goal is to create powerful yet modular imaging platforms that enable biologists to focus on discovery rather than instrument complexity, accelerating the adoption of advanced volumetric imaging techniques.

-----------

**Publication**
=========================

`Haug et al., 2025 (eLife 14:RP106910) <https://doi.org/10.7554/eLife.106910>`_ describes Altair-LSFM as a high-resolution, sample-scanning, open-source light-sheet microscope designed for subcellular imaging with straightforward assembly and reproducible alignment.

In bead-based benchmarking, Altair-LSFM achieved average FWHM values of 328 nm (x), 330 nm (y), and 464 nm (z) before deconvolution, improving to 235.5 nm (x), 233.5 nm (y), and 350.4 nm (z) after deconvolution across a 266 µm field of view. The manuscript further demonstrates fixed-cell imaging of nuclei, microtubules, actin filaments, and Golgi, as well as live-cell imaging of microtubules and vimentin in migrating cells.

--------

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
   hardware/index.rst
   getting_started/getting_started.rst
   future/index


.. toctree::
   :caption: Altair-SPIM v1
   :maxdepth: 2

   design_principles/design_process
   physical_assembly/physical_assembly
   system_characterization/system_characterization
   imaging/imaging
   live_cell/live_cell


.. toctree::
   :caption: Altair-ASLM/CTASLM/SPIM v1
   :maxdepth: 2

   baseplate2/baseplate2
   baseplate2_alignment/baseplate2_alignment
   baseplate2_exampleimages/baseplate2_exampleimages



**Authors**
============
Dr. John Haug performed all simulations, design, testing, and validation of Altair. Seweryn Gałecki and Hsin-Yu Lin
provided cells for testing imaging performance and assisted in their visualization. Xiaoding Wang assisted in
imaging and software performance. Dr. Kevin Dean oversaw and provided feedback on all research operations. This
project also benefited from valuable feedback from the **Dean, Fiolka, and Danuser labs** at **UTSW**.

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
