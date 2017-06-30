###########
Audiohealth
###########


************
Introduction
************
The people around `Open Source Beehives (OSBH) <https://opensourcebeehives.com/>`_ were directing towards audio from the very beginning and therefore presenting coefficients which where won via `machine learning <https://github.com/opensourcebeehives/MachineLearning-Local>`_, learned via the `audio-samples <https://www.dropbox.com/sh/us1633xi4cmtecl/AAA6hplscuDR7aS_f73oRNyha?dl=0>`_ they had so far.

The promising output is simply the activity/health status of a bee colony! So far it can tell whether they are dormant, active, pre-, post- or swarming, if the queen is missing or hatching. For more background information about the audio processing, please follow up reading
`current work status thread in the OSBH Forum <https://community.akerkits.com/t/main-thread-current-work-status/326>`_.


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
Install some distribution software packages::

    apt install python-scipy python-numpy sox youtube-dl

Build the `osbh-audioanalyzer <https://github.com/hiveeyes/osbh-audioanalyzer>`_::

    cd tools/osbh-audioanalyzer/
    ./build.sh
    cd ../..


Main program
============
::

    virtualenv --system-site-packages venv27
    source venv27/bin/activate
    python setup.py install


*****
Usage
*****
::

    audiohealth --file ~/audio/samples/swarm_-15_-5.ogg --analyzer tools/osbh-audioanalyzer/bin/test


*******
Credits
*******
The driving force behind the audio signal processing at OSBH is `Javier Andrés Calvo <https://github.com/Jabors>`_, so we want to send a big thank you to him and the whole OSBH team - this program is really standing on the shoulders of giants. Keep up the good work!
