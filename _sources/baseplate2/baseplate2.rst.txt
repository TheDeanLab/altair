.. _aslmbaseplate-home:

##############
Altair ALSM/CTASLM Baseplate
##############

---------------

Overview
______________________

The second iteration of our Altair LSFM baseplate incorporates 3 different microscope configurations:
    1. Traditional Sample-Scanning SPIM
    2. Sample-Scanning Axially-Swept Light Sheet Microscope (ASLM)
    3. Sample-Scanning Cleared-Tissue ASLM (CTASLM)

Where each of these microscope paths incorporate as many of the same elements as possible between them, such that
switching or upgrading between these modes is as accessible as possible and doesn't require repurchasing all
components along their respective illumination paths.

The primary distinction between ASLM/CTASLM and our SPIM paths is the incorporation of a remote focusing objective (RFO)
system into the illumination path itself. The RFO system essentially allows the light sheet focus to be swept across
the full field of view (FoV) of your imaging sensor, in comparison to the traditional SPIM system which is limited to a
thin line profile on the imaging sensor. More information on ASLM can be found `here <https://www.nature.com/articles/s41596-022-00706-6>`_.

.. figure:: Images/ASLMIntro.png
    :align: center
    :alt: Images showing the ability of the RFO in ASLM to sweep the light sheet focus across a camera FoV

    **Figure 1:** (Left) A schematic of how the focus of the light sheet is swept and synced with the rolling shutter
        of an associated camera system in ASLM. (Right) Two different images taken where the top image is taken without
        utilizing the RFO and the bottom is utilizing the RFO, where when it's utilized the beam is able to be swept across
        the full FoV of the image.

----------------


Zemax Simulation Setup Process
______________________________

With our chosen lenses in mind, we can download Zemax files associated with each lens directly from Thorlabs website
and set up our simulation.

.. figure:: Images/Atlair_ASLM_Path.png
    :align: center
    :alt: Setup of the Zemax simulations

    **Figure 2:** Setup of the ASLM-based Zemax simulations, where the forward and reverse paths from the RFO are
        unfurled to a single path.



