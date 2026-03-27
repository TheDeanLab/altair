.. _dvopmoverview-home:

##############################
Introduction
##############################

Direct-View OPM
_______________

The Direct-View OPM (dvOPM) system is an oblique-plane light-sheet microscopy technique designed for mesoscopic fluorescence imaging of large specimens. In this approach, an oblique imaging plane within the sample is optically sectioned using a light sheet and directly projected onto a camera sensor.

Conventional oblique-plane microscopy systems typically rely on a tertiary imaging objective to re-image the tilted plane onto the detector. In contrast, dvOPM eliminates this requirement by projecting the oblique image plane directly onto a compact camera sensor using a simplified relay. This reduces optical complexity and system footprint while preserving the optical sectioning capability of light-sheet microscopy.

As a result, dvOPM provides a practical approach for imaging extended fields of view with optical sectioning while maintaining a compact and accessible optical design.

------------------------------

System Overview
_______________

The dvOPM system consists of separate illumination and detection optical trains arranged around a shared sample region in an inverted configuration, where both illumination and detection are performed from below the specimen.

The illumination subsystem generates a light sheet that intersects the sample at an oblique angle relative to the imaging stage. Fluorescence emitted from this illuminated plane is collected by the primary objective and relayed through the detection optics, which project the tilted image plane directly onto the camera sensor.

Image acquisition is performed using a stage-scanning geometry, in which the sample is translated through the stationary illumination and detection planes to acquire volumetric data without moving the optical components.

The illumination and detection subsystems are implemented as independent modular assemblies mounted on precision baseplates. The detection module is mounted on a vertically oriented translation stage, allowing adjustment of the imaging plane relative to the sample while preserving the fixed optical geometry of the relay.

------------------------------

Altair dvOPM
____________

The Altair dvOPM implementation focuses on translating the dvOPM concept into a system that is easier to construct, align, and reproduce.

The detection path uses a pair of commercially available photographic lenses to form the remote image directly on the camera sensor, eliminating the need for complex multi-objective relay systems. Both the illumination and detection subsystems are implemented as modular baseplate assemblies, where the optical layout is mechanically constrained based on optimized design parameters.

This approach reduces alignment sensitivity, limits the number of adjustable degrees of freedom, and improves reproducibility of the system. By combining simplified optical design with structured mechanical implementation, the Altair dvOPM provides a practical and accessible realization of oblique-plane light-sheet microscopy.

------------------------------

The detailed optical design and implementation of the detection and illumination subsystems are described in the following section.