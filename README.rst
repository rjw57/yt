``yt``: a command-line YouTube client
=====================================

``yt`` is a command-line front-end to YouTube which allows you to browse YouTube
videos and play them directly from the command-line. It uses ``youtube-dl`` and
``mplayer`` or ``omxplayer`` to actually *play* the videos.

The combination of a text based interface and ``omxplayer`` makes ``yt`` a great
YouTube client for the Raspberry Pi.

Usage
-----

Launch using ``mplayer`` with::

    yt

or, if you're using a Raspberry Pi, using ``omxplayer``::

    pi-yt

Installation
------------

From PyPi (easier!)
~~~~~~~~~~~~~~~~~~~

::

    # Install dependancies
    sudo apt-get install youtube-dl
    # Ensure using latest version of youtube-dl to keep up with YouTube API changes
    sudo youtube-dl -U

    # Install from PyPi
    sudo apt-get install python-setuptools
    sudo easy_install whitey

From GitHub
~~~~~~~~~~~

::

    # Install dependancies
    sudo apt-get install youtube-dl
    # Ensure using latest version of youtube-dl to keep up with YouTube API changes
    sudo youtube-dl -U

    # Install from GitHub
    sudo apt-get install python-setuptools
    git checkout git@github.com:rjw57/yt.git
    cd yt
    sudo python setup.py install

Usage
-----

::

    usage: yt [-h] [--player {mplayer,omxplayer}]

    optional arguments:
      -h, --help            show this help message and exit
      --player {mplayer,omxplayer}
                            specifies what program to use to play videos (default:
                        mplayer)
                        
Dependancies
------------

- youtube-dl
- mplayer or omxplayer
                        
Common problems
---------------

Videos don't play when selected in interface
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Make sure you have the latest version of youtube-dl. youtube-dl has a self update
mechanism::

    sudo youtube-dl -U

Omxplayer starts and terminates without playing video
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For high quality videos the default memory allocation on the Raspberry Pi doesn't
provide enough memory to the GPU.

The default 192M ARM, 64M GPU split can be changed to a 128M ARM, 128M GPU split
using raspi-config.

::

    sudo raspi-config
    # Select memory-split
    # Allocate 128M to the GPU
        
See http://elinux.org/RPi_Advanced_Setup for more information.

Getting more help
~~~~~~~~~~~~~~~~~

See https://github.com/rg3/youtube-dl and https://github.com/huceke/omxplayer for
more detailed help.


Credits
-------

- `Distribute`_
- `Buildout`_
- `modern-package-template`_
- `youtube-dl`_
- `mplayer`_
- `Omxplayer`_
- Mark Baldridges's "HOWTO: YouTube on the Raspberry Pi - sans X)" - http://www.raspberrypi.org/phpBB3/viewtopic.php?p=97710&sid=fa3272a732353dc501cb96d38453b97c#p97710

.. _Buildout: http://www.buildout.org/
.. _Distribute: http://pypi.python.org/pypi/distribute
.. _`modern-package-template`: http://pypi.python.org/pypi/modern-package-template
.. _`youtube-dl`: http://rg3.github.com/youtube-dl/
.. _`mplayer`: http://www.mplayerhq.hu/
.. _`Omxplayer`: https://github.com/huceke/omxplayer
