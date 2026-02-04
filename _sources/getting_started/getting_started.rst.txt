.. _gettingstarted-home:

###############
Getting Started
###############

In order to be able to control stage positions (which are used for focus and sample positioning), toggle lasers, trigger cameras, and so on, 
you first need to set up a connection to your hardware. This guide will walk you through the steps necessary to get your system up and running.

Hardware Setup
______________________

Unlike other microscopy systems, Altair simplifies control by having only one controller - one apparatus to trigger and drive all necessary devices. 
This is Applied Scientific Instrumentation's Tiger Controller, a modular controller with customizable control cards.
Our solution calls for a tiger controller with the following cards:
- 	TGCOM - allows Joystick control and serial communication from computer
-	3 Stage control cards - (X/Y, Z/F, M/N)
-	2 DAC4 cards - Analog signal generators
-	TGPLC - Programmable Logic Controller which provides for custom timing
-	FW-1000 - Filter Wheel Control
The order of these cards within the controller does not matter.
The software to run the controller is `navigate <https://thedeanlab.github.io/navigate/index.html>`_.
Navigate supports many microscope configurations, where each configuration is defined by a configuration file.
The provided configuration file will delineate the following configuration:

=====  ============================
**Axis**   **Device**
=====  ============================
**A**      Remote Focus Voice Coil
**B**      Galvanometer
**H**      405 nm Laser (Analog)
**I**      488 nm Laser (Analog)
**J**      561 nm Laser (Analog)
**K**      638 nm Laser (Analog)
**1**      Camera Trigger
**2**      Laser Shutter
**3**      Stage In
**4**      Stage Out
**5**      405 nm Laser (Digital)
**6**      488 nm Laser (Digital)
**7**      561 nm Laser (Digital)
**8**      638 nm Laser (Digital)
=====  ============================


The stage control card specified for PLC outputs 3 and 4 is the stage that is used for Z-stacks. 
This allows stage feedback to dictate when the sample is ready for an image. 
In our configuration, the X hardware stage corresponds to the Z stage within the software. 
This can be changed to match your stage setup by editing the following part of the configuration file:

.. collapse:: Configuration File

    .. code-block:: yaml

      microscopes:
        microscope_name:
            stage:
              hardware:
                -
                  type: ASI
                  serial_number: 001
                  axes: [x, y, z, f]          # software stages 
                  axes_mapping: [X, Y, Z, F]  # hardware stages