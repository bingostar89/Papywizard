# -*- coding: iso-8859-1 -*-

""" Panohead remote control.

Configurations.

@author: Frédéric Mantegazza
@copyright: Frédéric Mantegaza (C) 2007-2008
@license: CeCILL
@todo:
"""

__revision__ = "$Id$"

import os.path


VERSION = "0.9beta2"
PACKAGE_VERSION = 2

GLOBAL_CONFIG_DIR = "/etc"
HOME_DIR = os.path.expandvars("$HOME")
USER_CONFIG_DIR = os.path.join(HOME_DIR, ".config") # OpenDesktop standard
try:
    os.mkdir(USER_CONFIG_DIR)
except OSError, (errno, errmsg):
    if errno == 17:
        pass
    else:
        raise
CONFIG_FILE = "papywizard.conf"
GLOBAL_CONFIG_FILE = os.path.join(GLOBAL_CONFIG_DIR, CONFIG_FILE)
USER_CONFIG_FILE = os.path.join(USER_CONFIG_DIR, CONFIG_FILE)

SENSOR_RATIOS = {'3:2': 3./2., '4:3': 4./3.}
SENSOR_RATIOS_INDEX = {'3:2': 0, '4:3': 1,
                       0: '3:2', 1: '4:3'}
DEFAULT_SENSOR_RATIO = "3:2"

CAMERA_ORIENTATION_INDEX = {'portrait': 0, 'landscape': 1,
                            0: 'portrait', 1: 'landscape'}

MOSAIC_TEMPLATE = ["Auto",
                   "RDL", "RDR", "RUL", "RDR",
                   "LDR", "LDL", "LUR", "LUL",
                   "DRU", "DRD", "DLU", "DLD",
                   "URD", "URU", "ULD", "ULU"
                   ]
