.. _dvopmoverview-home:

##############################
Introduction
##############################

Direct-View OPM
_______________

The Direct-View OPM (dvOPM) system is an oblique-plane light-sheet microscope designed for mesoscopic fluorescence imaging of large specimens. The system projects an oblique image plane directly onto a compact camera sensor without the use of a tertiary objective, simplifying the remote-imaging path while preserving light-sheet optical sectioning. This architecture enables a compact detection path while preserving the optical sectioning advantages of light-sheet microscopy.

------------------------------

System Overview
_______________

The dvOPM system consists of independent illumination and detection optical trains arranged around a shared sample region. The illumination subsystem generates an oblique The light sheet intersects the specimen at an oblique angle relative to the imaging stage, while the emitted fluorescence is captured by the primary objective and relayed through the detection optics, which project the tilted image plane directly onto the camera sensor.

The microscope operates using a stage-scanning acquisition geometry, where the specimen is translated through the stationary illumination and detection planes to acquire volumetric data. The illumination and detection optics are implemented as independent modular assemblies mounted on precision baseplates. The detection module is attached to a vertically oriented translation stage that allows adjustment of the imaging plane relative to the specimen while maintaining the fixed optical geometry of the system.

------------------------------

Altair dvOPM
____________

The implementation presented here focuses on practical engineering improvements to simplify construction and alignment of the system. The detection path uses a pair of readily available photographic lenses to form the remote image directly on the camera sensor, while the illumination and detection subsystems are implemented as modular baseplate assemblies. These design choices reduce optical complexity, constrain alignment degrees of freedom, and support reproducible assembly within the Altair platform.

------------------------------