============
Introduction
============

.. _volumetric-imaging:

Why is Volumetric Imaging Important?
====================================

Biological processes occur in a fundamentally three-dimensional (3D) space, and the spatial organization of
molecular structures is critical to cellular function. Traditional two-dimensional (2D) imaging provides only
a limited cross-section of these dynamic events, often obscuring key interactions and leading to incomplete
or misleading interpretations.

For instance, during mitosis, chromosomes undergo intricate rotations within the entire cellular volume,
and microtubules dynamically polymerize and depolymerize as they engage and separate daughter
chromosomes at their kinetochores. In 2D imaging, these structures inevitably drift in and out of the focal
plane, making it challenging to track such dynamic processes over time. Similarly, in complex tissue
environments, organelle positioning, cell-cell interactions, and subcellular signaling pathways are all
inherently shaped by their 3D spatial context.

By capturing the full volume of a specimen, volumetric imaging enables a more accurate representation of
cellular architecture and dynamic molecular events. This is particularly critical for understanding
developmental biology, disease progression, and cellular interactions within their native environments.
Emerging technologies such as light-sheet microscopy, expansion microscopy, and advanced computational
imaging now allow researchers to visualize biological systems at unprecedented resolutions, bridging the
gap between molecular detail and tissue-scale organization.

---------------

.. _why-light-sheet:

The Importance of Parallelization
=================================

Historically, 3D imaging has been performed using spinning disk and laser scanning
confocal microscopes. However, these microscopes waste significant excitation
energy on out-of-focus regions, leading to unnecessary photodamage while requiring
compensatory increases in laser power due to their low illumination duty cycle. This problem
is further exacerbated by their sequential, point-by-point image acquisition, which limits
speed and increases photobleaching.

.. sidebar:: **Illumination Confinement**
   :class: sidebar-note

   **Illumination confinement** refers to the restriction of excitation light to within the **depth of focus** of the
   detection objective, ensuring that only light contributing to image formation is used. This is a key advantage of
   **light-sheet fluorescence microscopy (LSFM)**, where the illumination plane is matched to the detection plane,
   minimizing out-of-focus excitation and reducing phototoxicity.

In contrast, depending on their design, light-sheet fluorescence microscopes (LSFM)
restrict illumination primarily to the focal plane of interest, minimizing phototoxicity while
maximizing imaging efficiency. Additionally, by leveraging highly sensitive scientific cameras
(e.g., 4×10\ :sup:`6` pixels), LSFM enables massively parallelized image acquisition—recording
entire planes in a single exposure rather than scanning point-by-point.

For instance, a typical laser scanning confocal microscope requires **~4.16 s** to acquire
a **2048 × 2048** voxel image, given a voxel dwell time of **1 µs**. In contrast, an LSFM can
image the same region in just **~5 ms**, an **832-fold** increase in speed, all while maintaining a
**5,000-fold longer** per-voxel dwell time. This extended dwell time enables improved signal
accumulation, lower laser power requirements, and a significantly improved signal-to-noise
ratio (SNR). As a result, LSFM is uniquely suited for long-term volumetric imaging at high
spatiotemporal resolution while reducing photodamage.

.. sidebar:: **Spatial Duty Cycle**
   :class: sidebar-note

   The **spatial duty cycle of illumination** refers to the fraction of a sample that is actively contributing to
   image formation at any given moment during an imaging process. In **laser scanning confocal microscopy**,
   only a single point is illuminated at a time, resulting in a **low duty cycle** and requiring compensatory increases in laser
   power to maintain signal. In contrast, **light-sheet fluorescence microscopy (LSFM)** illuminates and images an entire plane at once,
   yielding a **duty cycle** that approaches 100%, enabling drastically reduced laser powers that reduce phototoxicity.


---------------

.. _challenges:

Challenges with 3D Imaging
==========================

To extract meaningful biological insight from volumetric imaging, microscopes must achieve
sufficient **spatiotemporal resolution** while preserving molecular specificity and compatibility with advanced
analytical techniques. This requires integration with biosensors, opto- and chemogenetic tools, and
computer vision analyses that translate **high-dimensional 5D datasets** (x, y, z, :math:`\lambda`, t) into
quantitative biological readouts. Several key challenges must be addressed to ensure the accuracy and
reliability of 3D imaging:

-   **Nyquist Sampling in Space and Time:**
    To faithfully capture dynamic processes, the event of interest must be **Nyquist sampled** in both
    spatial and temporal dimensions. For example, the GTPase cycle times of Rho, Rac, and Cdc42 can be
    as short as 5 s, necessitating volumetric acquisitions at :math:`\leq` 2.5 s per volume with a spatial resolution
    of **<500 nm**. Furthermore, resolution should ideally be **isotropic or nearly isotropic** to prevent
    morphology-dependent intensity artifacts—particularly for signaling events at the plasma membrane.

-   **Multicolor Excitation and Detection:**
    To enable multiplexed cellular readouts, the microscope must support **simultaneous multicolor imaging**
    with achromatic performance across excitation and detection wavelengths. Microscope designs that
    rely on spatial light modulators (SLMs) for excitation often struggle to achieve this, as the diffraction
    efficiency of SLMs varies with wavelength.

-   **Detection Sensitivity and Phototoxicity:**
    Imaging performance must be **photon-efficient** to minimize the need for high ectopic expression of
    signaling-active proteins and to mitigate **photobleaching and phototoxicity**—a challenge that
    is amplified when acquiring **10–100 slices per volume**. Maximizing quantum efficiency and minimizing
    out-of-focus excitation are crucial for maintaining live-cell viability.

-   **Field of View Constraints:**
    When imaging dynamic processes in **extracellular matrix environments** (where cells can migrate in
    any direction) or within a **developing embryo**, the microscope must provide a sufficiently **large field
    of view (FOV)**—ideally **>100 × 100 × 100 µm**. Many leading **light-sheet fluorescence microscopes
    (LSFMs)** are optimized for small fields of view (e.g., 25 µm), which limits their applicability to studies
    of large-scale tissue dynamics.

-   **Avoidance of Computational Post-Processing Biases:**
    To ensure compatibility with **quantitative downstream analyses**, reliance on iterative **deconvolution**
    or structured illumination routines should be minimized. These techniques can introduce statistical
    artifacts that distort numerical analyses, particularly when measuring intensity distributions, localization
    precision, or dynamic molecular interactions.

.. sidebar:: **Nyquist Sampling**
   :class: sidebar-note

   **Nyquist sampling** is a fundamental principle in signal processing that dictates the minimum sampling
   frequency required to accurately reconstruct a signal without aliasing. According to the **Nyquist-Shannon
   sampling theorem**, a continuous signal must be sampled at least **twice the highest frequency component**
   present in the signal to ensure faithful reconstruction.

   In microscopy, Nyquist sampling applies to both **spatial and temporal domains**:

   - **Spatial Nyquist Sampling:** To accurately resolve features of size :math:`d`, the sampling interval
     (pixel or voxel spacing) should be no greater than :math:`d/2`. This ensures that high-frequency
     structural details are captured without loss of information.

   - **Temporal Nyquist Sampling:** To track dynamic processes occurring at a characteristic frequency
     :math:`f_c`, images must be acquired at a frequency of :math:`\geq 2 \times f_c` to prevent
     aliasing in time-lapse imaging.

   Failure to meet the Nyquist criterion results in **aliasing**, where high-frequency components are misrepresented
   as lower-frequency artifacts, distorting biological measurements.

Meeting these criteria is essential for **accurate, high-throughput volumetric imaging** that captures
cellular dynamics with sufficient fidelity to support rigorous biological interpretation.


---------------

.. _why-build:

Why Build a Microscope?
========================

The technology required to achieve **multiplexed volumetric imaging** with advanced probes and computer vision
analyses already exists. However, the commercialization process imposes significant constraints on innovation.
Microscope manufacturers prioritize **aesthetically attractive, highly engineered, and serviceable optical
systems** that ensure a large return on investment. As a result, they tend to be **extremely conservative** in
adopting emerging technologies.

Most commercially available microscopes take **over seven years** to develop, by which time they are often
already obsolete due to rapid scientific advancements. A notable exception is the **Lattice Light-Sheet Microscope
(LLSM)**, which was sublicensed by Zeiss to 3i shortly after its seminal publication. However, even in this case,
it took another **six years** for Zeiss to release a consumer-friendly model—at a prohibitive cost of **~$1M USD**.

Beyond commercialization delays, **patent restrictions** further stifle innovation. The **highly fragmented and
entangled intellectual property (IP) landscape** makes it difficult for new start-ups to enter the market. For
example, despite their own **limited role in developing oblique plane microscopy (OPM)**, Leica has exclusively
licensed a patent for **off-axis tertiary imaging systems**, effectively blocking broader commercialization of OPM.

As a result, reliance on commercial microscope development not only **delays technology adoption** but can
actively **impede the dissemination of transformative imaging methods**. This reality makes in-house development
of custom microscopy platforms essential for pushing the frontiers of biological imaging forward.
