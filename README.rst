``yt``: a command-line YouTube client
=====================================

``yt`` is a command-line front-end to YouTube which allows you to browse YouTube
videos and play them directly from the command-line. It uses ``youtube-dl`` and
``mplayer`` or ``omxplayer`` to actually *play* the videos.

The combination of a text based interface and ``omxplayer`` makes ``yt`` a great
YouTube client for the Raspberry Pi.

Installation
------------

1. Install setup tools. Eg. on a Debian based distro `sudo apt-get install python-setuptools`.
2. From top level directory run `python setup.py install`.

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

Make sure you have the latest version of youtube-dl. The latest version in a package repository
may lag significantly behind ongoing changes to YouTube. You can get the latest version
by downloading youtube-dl directly from the GitHub repository.

Quick install instructions::

    wget https://github.com/rg3/youtube-dl/blob/master/youtube-dl?raw=true
    chmod +x youtube-dl
    sudo mv youtube-dl /usr/bin/youtube

Omxplayer starts and terminates without playing video
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For high quality videos the default memory allocation on the Raspberry Pi doesn't
provide enough memory to the GPU.

The default 192M ARM, 64M GPU split can be changed to a 128M ARM, 128M GPU split
by swapping the GPU firmware images.

::

    sudo cp /boot/arm128_start.elf /boot/start.elf.
        
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
