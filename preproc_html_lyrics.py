#!/usr/bin/env python
"""This script processes the lyrics files from
https://www.cygnus-x1.net/links/rush/albums-... to prepare them as input to a
text generation program"""

from html.parser import HTMLParser

INPUT_FILE_LIST = ['albums-2112.php', 'albums-afarewelltokings.php',
                   'albums-caressofsteel.php', 'albums-clockworkangels.php',
                   'albums-counterparts.php', 'albums-feedback.php',
                   'albums-flybynight.php', 'albums-graceunderpressure.php',
                   'albums-hemispheres.php', 'albums-holdyourfire.php',
                   'albums-movingpictures.php', 'albums-myfavoriteheadache.php',
                   'albums-permanentwaves.php', 'albums-powerwindows.php',
                   'albums-presto.php', 'albums-rollthebones.php',
                   'albums-rush.php', 'albums-signals.php',
                   'albums-snakesandarrows.php', 'albums-testforecho.php',
                   'albums-vaportrails.php', 'albums-victor.php']
