.. _voicecoil-home:

###############################
Remote Focus Actuator
###############################

In Axially Swept Light-Sheet Microscopy (ASLM), axial scanning is achieved by driving a mirror placed at the focus of a remote objective. To maintain high-fidelity imaging, the remote focus actuator must precisely synchronize its motion with the rolling shutter of the camera. However, designing for speed and accuracy involves trade-offs. As the stroke of the actuator increases, its mechanical bandwidth decreases, limiting the maximum acquisition rate for large field of view imaging. Similarly, higher scan frequencies tend to reduce the scan amplitude and introduce phase delays, which can degrade image quality, especially at the edges of the field of view. Therefore, it is crucial to select an actuator that balances these factors effectively.

Early implementations of ASLM used piezoelectric actuators, but modern systems often employ voice coil actuators for improved performance. We have tested two commercially available systems: the LFA2004 from Equipment Solutions and the Blink from Thorlabs. The LFA2004 is reliable, easy to configure, and sufficient for most imaging applications, while the Blink offers higher performance at the cost of greater complexity and sensitivity to tuning. For most users, we recommend the LFA2004.

When ordering the LFA2004, we typically request the stage configured with the SCA814 amplifier and SPS15 power supply. For standard ASLM configurations, we recommend tuning the system for a ~2 gram mirror with a 30 µm sawtooth waveform (90% duty cycle). The factory can preconfigure the unit to accept an analog position command by default (servo active). If oscillation or high-frequency noise is observed when the servo is engaged, you can fine-tune the control loop via the RS232 interface by adjusting the “A” and “B” parameters. A common stable configuration is A 40 20 and B 80 5, though slight adjustments may be necessary depending on your optical load and mechanical setup.
