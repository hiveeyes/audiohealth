########################################
Bee colony vitality using audio analysis
########################################


************
Introduction
************
The people around `Open Source Beehives (OSBH) <https://opensourcebeehives.com/>`_ were directing towards audio from the very beginning and therefore presenting coefficients which where won via `machine learning <https://github.com/opensourcebeehives/MachineLearning-Local>`_, learned via the `audio-samples <https://www.dropbox.com/sh/us1633xi4cmtecl/AAA6hplscuDR7aS_f73oRNyha?dl=0>`_ they had so far.

The output is simply the activity/health status of a bee colony. So far the algorithm can tell whether the colony is dormant, active, pre-, post- or swarming, if the queen is missing or hatching. For more background information about the audio processing, please follow up reading
`current work status thread in the OSBH Forum <https://community.akerkits.com/t/main-thread-current-work-status/326>`_.
So far, the results are promising.


*******
Details
*******
We forked the "`OSBH machine learning <https://github.com/opensourcebeehives/MachineLearning-Local>`_" repository to `osbh-audioanalyzer <https://github.com/hiveeyes/osbh-audioanalyzer>`_ to make it able to obtain an input file option. The wrapper script resides in the [audiohealth] repository.

For more information, see also `Rate vitality of bee colony via analysing its sound <https://community.hiveeyes.org/t/rate-vitality-of-bee-colony-via-analysing-its-sound/357/6>`_.


*****
Usage
*****

Synopsis
========
::

    audiohealth --audiofile ~/audio/samples/colony_before_swarming_25_to_15.ogg --analyzer tools/osbh-audioanalyzer/bin/test

Output::

    ==================
    Sequence of states
    ==================
    pre-swarm, pre-swarm, pre-swarm, pre-swarm, pre-swarm, pre-swarm, pre-swarm, pre-swarm, pre-swarm, active, active, active, active, active, active, active, active, active, active, pre-swarm, pre-swarm, pre-swarm, pre-swarm, pre-swarm, pre-swarm, pre-swarm, pre-swarm, pre-swarm, pre-swarm, pre-swarm, pre-swarm, pre-swarm, active, active, active, active, active, active, active, pre-swarm, active, pre-swarm, pre-swarm, pre-swarm, pre-swarm, active, active, active, active, pre-swarm, pre-swarm, active, active, pre-swarm, active, pre-swarm, active, active, active, pre-swarm,

    ===================
    Compressed timeline
    ===================
      0s -  80s   pre-swarm       ========
     90s - 180s   active          =========
    190s - 310s   pre-swarm       ============
    320s - 380s   active          ======
    390s - 400s   pre-swarm       =
    400s - 410s   active          =
    410s - 440s   pre-swarm       ===
    450s - 480s   active          ===
    490s - 500s   pre-swarm       =
    510s - 520s   active          =
    530s - 540s   pre-swarm       =
    540s - 550s   active          =
    550s - 560s   pre-swarm       =
    560s - 580s   active          ==
    590s - 600s   pre-swarm       =

    ==============
    Total duration
    ==============
           320s   pre-swarm       ================================
           280s   active          ============================

    ======
    Result
    ======
    The most common events (i.e. the events with the highest total duration) are:

         The colony is mostly in »PRE-SWARM« state, which is going on for 320 seconds.
         Sometimes, the state oscillates to »ACTIVE«, for 280 seconds in total.

    ==========
    Disclaimer
    ==========
    THERE IS NO WARRANTY FOR THE PROGRAM, TO THE EXTENT PERMITTED BY APPLICABLE LAW. NO LIABILITY FOR ANY DAMAGES WHATSOEVER.


Help
====
::

    $ audiohealth --help
        Usage:
          audiohealth --audiofile audiofile --analyzer /path/to/osbh-audioanalyzer [--strategy lr-2.0] [--debug] [--keep]
          audiohealth --datfile datfile --analyzer /path/to/osbh-audioanalyzer [--strategy lr-2.0] [--debug]
          audiohealth --version
          audiohealth (-h | --help)

        Options:
          --audiofile=<audiofile>   Process audiofile. Please use sox-compatible input formats.
          --datfile=<datfile>       Process datfile.
          --analyzer=<analyzer>     Path to OSBH audioanalyzer binary
          --strategy=<strategy>     The classification strategy. One of dt-0.90, dt-0.91, dt-1.0, dt-2.0, lr-2.0
          --keep                    Keep (don't delete) downsampled and .dat file
          --debug                   Enable debug messages
          -h --help                 Show this screen


Hint: By using ``--strategy dt-2.0`` or even ``--strategy dt-1.0``, different
classification strategies can be toggled to be able to compare results against each other.
``"dt-"`` means "decision tree", while ``"lr-"`` means "logistic regression".

The cutting edge classification strategy is ``"lr-2.0"``, which is also the default setting.
See also commit `Added new filters and logistic regression classifier <https://github.com/opensourcebeehives/MachineLearning-Local/commit/a40de504>`_. Aaron Makaruk describes it on 2017-07-01 like:

    Our classifier has been recently updated to include two new states, and we've moved past decision-tree algorithms to something yielding greater results.



*****
Setup
*****

Repository
==========
::

    git clone --recursive https://github.com/hiveeyes/audiohealth
    cd audiohealth


Prerequisites
=============
To relieve your machine from compiling SciPy or NumPy, install the python libraries from your distribution. `audiohealth` furthermore relies on `sox <http://sox.sourceforge.net/Docs/Documentation>`_ for audio resampling.
We also recommend `youtube-dl <http://youtube-dl.org/>`_ for downloading audio samples from Youtube.

Install some distribution software packages::

    apt install python-scipy python-numpy sox libsox-fmt-all youtube-dl

Build the `osbh-audioanalyzer <https://github.com/hiveeyes/osbh-audioanalyzer>`_::

    cd tools/osbh-audioanalyzer/
    ./build.sh
    cd ../..


Main program
============
::

    virtualenv --system-site-packages .venv27
    source .venv27/bin/activate
    python setup.py develop


*******
Credits
*******
The driving force behind the audio signal processing at OSBH is `Javier Andrés Calvo <https://github.com/Jabors>`_, so we want to send a big thank you to him and the whole OSBH team - this program is really standing on the shoulders of giants. Keep up the good work!

