<h1 align="center">
altair

<img 
	src="https://github.com/TheDeanLab/altair/blob/main/docs/source/general/compass.png?raw=true"
  	alt="altair"
  	width="250"
/>

<h3 align="center">
	Cost-Effective, Open-Source, Light-Sheet Microscopy Solutions for Sub-Cellular Imaging.
</h3>
</h1>

[![eLife Article](https://img.shields.io/badge/eLife-Article%20106910-0B7285)](https://elifesciences.org/articles/106910)
[![DOI](https://img.shields.io/badge/DOI-10.7554%2FeLife.106910-1f6feb)](https://doi.org/10.7554/eLife.106910)
[![Zenodo DOI](https://zenodo.org/badge/796858312.svg)](https://doi.org/10.5281/zenodo.18060763)

**Altair** aims to democratize high-resolution light-sheet fluorescence microscopy. By combining **modular optomechanics**, **cutting-edge lens simulations**, and **intelligent software**, **Altair** enables the rapid assembly of high-performance light-sheet microscopes in a user-friendly package.

As reported in our eLife publication, Altair-LSFM is a high-resolution, sample-scanning light-sheet microscope that uses an in-silico optimized optical train and a custom-machined baseplate to simplify alignment. In bead-based benchmarking, Altair-LSFM achieved average FWHM values of 328 nm (x), 330 nm (y), and 464 nm (z) before deconvolution, improving to 235.5 nm (x), 233.5 nm (y), and 350.4 nm (z) after deconvolution across a 266 um field of view.

## Publication

- Haug J, Galecki S, Lin H-Y, Wang X, Dean KM. *A high-resolution, easy-to-build light-sheet microscope for subcellular imaging.* eLife. 2025;14:RP106910. [https://doi.org/10.7554/eLife.106910](https://doi.org/10.7554/eLife.106910)

## Motivation

Cellular behavior is orchestrated by diverse signaling mechanisms that often hinge on **molecular events precisely organized in space and time**. These events include rapid, localized protein interactions that drive processes such as cell division, migration, and differentiation. **Altair** addresses the need for **high-resolution live-cell imaging**, empowering researchers to:

- Visualize spatially regulated processes.
- Collect quantitative 3D time-lapse data.
- Bridge molecular probe design and advanced computational image analysis.

## Goal

The overarching goal is to provide a **modular, cost-effective 3D light-sheet microscope** that:
- Can be assembled with minimal prior optics expertise.
- Delivers ~235 nm lateral and ~350 nm axial resolution after deconvolution (~328/330 nm in XY and ~464 nm in Z before deconvolution) across a 266 um field of view.
- Seamlessly integrates with our user-friendly, **intelligent imaging software** [navigate](https://github.com/TheDeanLab/navigate).
- Streamlines data acquisition, drastically reducing barriers to cutting-edge microscopy.

## Key Features

1. **High-Resolution Optics**  
   - Optical designs extensively **simulated in Ansys Zemax OpticStudio** to ensure robust performance across the visible spectrum.
   - Thorough **tolerance analysis** to maintain alignment and resolution in non-specialist environments.

2. **Rugged Mechanical Design**  
   - **Computer aided design (CAD) with Autodesk Inventor** for stress testing and mechanical reliability.
   - **Xometry** manufacturing ensures precision component fabrication.
   - **Dowel pins** and **Thorlabs Polaris mounts** allow reproducible alignment of optical elements.

3. **Easy-to-Source Components**  
   - Optics primarily sourced from **Thorlabs**, with **Polaris mounts** for stable positioning.
   - Motion control solutions (X, Y, Z, Focus, Sample Scanning) from **Applied Scientific Instrumentation**.
   - Open-hardware ethos with minimal custom parts to reduce cost and wait times.
   - Detailed step-by-step assembly instructions,

4. **Intuitive Control Software**  
   - Built to interface seamlessly with [navigate](https://github.com/TheDeanLab/navigate).
   - Automated routines for calibration, 3D volume acquisition, and intelligent imaging.


## Getting Started

- **Review the [Documentation](https://thedeanlab.github.io/altair/)**
- **Procure Hardware**
- **Download and Install** [navigate](https://github.com/TheDeanLab/navigate)
- **Assemble Hardware**
- **Optimize Alignment**
- **Validate Performance**


## Authors

- John Haug, Ph.D.
- Kevin M. Dean, Ph.D.

## Funding

- **UTSW-UNC Center for Cell Signaling Analysis**  NIH NIGMS RM1GM145399
- **Center for Metastatic Tumor Imaging**  NIH NCI U54CA268072
