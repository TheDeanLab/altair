.. _dvopmcharacterization-home:

##############################
Altair DV-OPM Characterization
##############################

To characterize the performance of the Altair DV-OPM, we evaluated the performance of the illumination train by imaging the sheet profile, and we also imged 1um fluorescent beads to quantify the resolution of the system.

---------------

Beam Characterization
_____________________

To characterize the beam profile of the illumination train, we imaged the sheet profile in air at a range of axial positions.

To characterize the illumination beam, we imaged the light sheet in air while translating the camera through a series of axial positions along the propagation direction, $Y'$. We then selected a fixed lateral region near the center of the sheet, so that the thickness measurement was made from the same representative part of the sheet at every axial position.

For each axial plane, the background-corrected intensity profile along the sheet thickness direction, $Z'$, was extracted and fit with a Gaussian function. The fitted Gaussian standard deviation, $\sigma$, was converted to FWHM using $\mathrm{FWHM}=2.35\sigma$ after applying the camera pixel size. The FWHM was subsequently converted to the Gaussian beam waist, $w$, using $w=\mathrm{FWHM}/\sqrt{2\ln2}$, where $w$ corresponds to the $1/e^2$ intensity radius. The best-focus plane was defined as the axial position with the minimum FWHM. From this plane, we measured an FWHM of $17.1~\mu\mathrm{m}$, corresponding to $w_0=14.53~\mu\mathrm{m}$.
We directly measured the usable axial distance from the experimental waist curve as the range over which $w(Y') \leq \sqrt{2}w_0$, giving a usable distance of approximately $2.00~\mathrm{mm}$.

.. figure:: Images/Axial_Thickness_Intensity.jpg
    :align: center
    :alt: Sheet profile characterization.

    **Figure 1:** Characterization of the light sheet profile in air along the axial direction.

At the best-focus plane, we also characterized the spatial distribution of the sheet. A representative image was used to show the light sheet morphology and its long lateral extent along $X'$. The normalized background-corrected intensity profile along $Z'$ reports the measured sheet thickness, while the lateral profile along $X'$ was calculated by summing the background-corrected intensity along $Z'$ at each lateral position. This provided a measure of the illumination distribution across the approximately $6.5~\mathrm{mm}$ lateral extent of the sheet.

.. figure:: Images/Focal_Plane.jpg
    :align: center
    :alt: Sheet profile characterization at focal plane.

    **Figure 2:** Characterization of the light sheet profile in air at the best-focus plane. A. Camera Image of the light sheet at the best-focus plane. B. Normalized intensity profile along the sheet thickness direction, $Z'$. C. Normalized intensity profile along the lateral direction, $X'$.

Beads
_____

To quantify the resolution of the system, we imaged 1um fluorescent beads embedded in agarose.

We imaged the beads at different axial positions along the propagation direction, $Y'$, and we measured the FWHM of the bead images along the lateral and axial directions to quantify the resolution of the system.

To prepare fluorescent bead samples, we diluted 1 µm YG nanosphere at a concentration of 1:1000 with deionized water and sonicated for 3 minutes to minimize aggregation. The resulting solution was later diluted at a concentration of 1:100 with 2% low-melting agarose for volumetric imaging.

.. figure:: Images/Beads_All.jpg
    :align: center
    :alt: Bead characterization.

    **Figure 3:** Image of 1um fluorescent beads embedded in agarose, imaged with the Altair DV-OPM. The beads are visible as bright spots against the dark background, and their size and shape can be used to quantify the resolution of the system.

.. figure:: Images/Beads_Single.jpg
    :align: center
    :alt: Bead characterization profiles.

    **Figure 4:** Single Zoomed-in Bead Image in XY and XZ planes.

We measured the full width at half-maximum (FWHM) values measured from images of 1 µm fluorescent beads (n = 302 beads), binned into 8 sections by lateral position across the field of view and the median values in each section are reported (in micrometers) for the X′, Y′ and Z′ directions. 

.. figure:: Images/Median_FWHM_final.svg
    :align: center
    :alt: Bead characterization profiles.

    **Figure 5:** Median FWHM values measured from images of 1 µm fluorescent beads, binned by lateral position across the field of view.

------------------------------