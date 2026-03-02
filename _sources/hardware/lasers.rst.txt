.. _lasers-home:

#############
Laser Sources
#############

When designing a microscope for imaging, the choice of light source is critical. In
general, an ideal imaging system will provide fast spectral switching, high light
throughput, stable power emission, a long lifetime, cost-effectiveness, and low
complexity.

Several light sources have been developed for use in microscopy, including arc lamps, light
emitting diodes (LEDs), solid state lasers (including fiber lasers, optically pumped
semiconductor lasers, diode pumped solid state lasers), supercontinuum lasers, and
ultrafast lasers (including Ti:sapphire lasers). A few key parameters to consider are
discussed below.

---------------

Linewidth
_________
One key aspect of any light source is the linewidth of its emission. This is the
spectral width of a light source in nanometers of the spectral density of the emitted
electric field. It can also be reported in wavenumbers (cm :sup:`-1`) or frequency (Hz).
Narrow linewidths enable more aggressive detection bands, reduced bleedthrough, and a
reduced background. LEDs typically have a linewidth of 20-50 nm, which is much broader
than the 0.1-1 nm linewidth of a laser. As such, we prefer lasers for our imaging
systems.

---------------

Beam Divergence
_______________
The M :sup:`2` value of a beam is the degree at which it can be focused to a given beam
divergence angle (e.g., numerical aperture). If you have a higher M :sup:`2` value of
~1.6, it will be focused to a laser spot that is 1.6x larger than the diffraction limit.
As such, for high-resolution imaging, it is important to have a low M :sup:`2` value.
We prefer lasers with an M :sup:`2` value of <1.2 for our imaging systems. Fiber lasers,
such as those offered by MPB Communications, provide very low M :sup:`2` values.
However, these systems require external mechanisms for controlling the power output,
which is a major disadvantage. For lasers with high M :sup:`2` values, additional
optics may be necessary to clean up the beam profile, such as a spatial filter.

---------------

Modulation
__________
The ability to modulate the power of a light source is important for many imaging
applications. It is not uncommon to use an acousto-optic modulator (AOM),
acousto-optic tunable filter (AOTF), or electro-optic modulator (EOM) to modulate the
power of a laser. AOMs induce sound waves within a crystal to change the refractive
index of the crystal, which alters the angle of the light at a single wavelength.
Likewise, AOTFs use a variable frequency sound wave to operate at multiple
wavelengths. EOMs, such as a Pockels cell, induce a directionally dependent
change in refractive index in a crystal, which can change the polarization of the
light passing through it. These are especially common in ultrafast laser systems.
Both AOMs and EOMs can be used to modulate the power of the laser, with
rise times of ~5-50 ns and ~0.25-1 ns, respectively. However, especially for continuous
wave (CW) lasers, these devices
serve as a source of additional complexity, cost, and potential failure points. For
example, we have noted that AOMs can be sensitive to temperature changes, which can
lead to drift in the power output. As such, we prefer lasers with built-in modulation
capabilities.

---------------

Vibrations
__________
Many lasers require active cooling, and are often placed directly on the optical table,
which can lead to vibrations. These vibrations can be detrimental to imaging quality,
especially when imaging in soft contexts such as expanded tissues. Nonetheless, if
insufficient cooling is provided, fluctuations in laser emission or instability can
occur.

---------------

Power
_____
The power of the laser that is needed depends critically on the light throughput of
the illumination train, as well as the size of the field of view. While some light
sources such as supercontinuum lasers can provide high power (e.g., >3 W), their emission
is spread across a large spectral range, reducing their spectral power density at any
given wavelength to a few mW/nm. We typically recommend lasers with a power of 100 mW
or greater for imaging.

---------------

Recommended Light Sources
-------------------------
For all of these reasons, we recommend the use of optically pumped semiconductor
lasers (OPSLs) for imaging. OPSLs are solid state lasers that use a diode to
optically pump a semiconductor gain medium which can be tuned to adjust the emission
wavelength of the laser. Importantly, OPSLs have a narrow linewidth (<10 pm), low M
:sup:`2` value, can modulate the laser on microsecond timescales, and achieve high
and stable emission powers.

OPSLs are available from several manufacturers and can typically be driven in either
a constant power or constant current mode. We typically use the former, as the laser
uses active feedback to stabilize the emission power. To eliminate challenges
associated with vibrations, we use single mode fiber-coupled OPSLs, which can be
removed from the optical table and provide excellent beam quality.

For our imaging systems, we have used the following lasers:

-   Coherent Galaxy laser combiner and OBIS lasers
-   Oxxius LaserBoxx with LuxX lasers.
-   Omicron LightHub Ultra with LuxX and OBIS lasers.
