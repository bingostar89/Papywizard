# -*- coding: utf-8 -*-

""" Panohead remote control.

License
=======

 - B{Papywizard} (U{http://www.papywizard.org}) is Copyright:
  - (C) 2007-2010 Frédéric Mantegazza

This software is governed by the B{CeCILL} license under French law and
abiding by the rules of distribution of free software.  You can  use,
modify and/or redistribute the software under the terms of the CeCILL
license as circulated by CEA, CNRS and INRIA at the following URL
U{http://www.cecill.info}.

As a counterpart to the access to the source code and  rights to copy,
modify and redistribute granted by the license, users are provided only
with a limited warranty  and the software's author,  the holder of the
economic rights,  and the successive licensors  have only  limited
liability.

In this respect, the user's attention is drawn to the risks associated
with loading,  using,  modifying and/or developing or reproducing the
software by the user in light of its specific status of free software,
that may mean  that it is complicated to manipulate,  and  that  also
therefore means  that it is reserved for developers  and  experienced
professionals having in-depth computer knowledge. Users are therefore
encouraged to load and test the software's suitability as regards their
requirements in conditions enabling the security of their systems and/or
data to be ensured and,  more generally, to use and operate it in the
same conditions as regards security.

The fact that you are presently reading this means that you have had
knowledge of the CeCILL license and that you accept its terms.

Module purpose
==============

Configurations.

@author: Frédéric Mantegazza
@copyright: (C) 2007-2010 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

import sys
import os.path

# Version
VERSION_MAJOR = 2
VERSION_MINOR = 1  # Odd means dev. release
VERSION_UPDATE = 20
VERSION = "%d.%d.%d" % (VERSION_MAJOR, VERSION_MINOR, VERSION_UPDATE)
VERSION_XML = "c"

# Find exact platform
platform = sys.platform
if platform == 'linux2':
    try:
        import PyQt4.QtMaemo5  # maemo 5?
    except ImportError:
        try:
            import hildon  # maemo 4?
        except ImportError:
            pass
        else:
            platform = "maemo"
    else:
        platform = "maemo"

# Paths
HOME_DIR = os.path.expanduser("~")
if sys.platform == 'win32':
    USER_CONFIG_DIR = os.path.join(os.path.expandvars("$APPDATA"), "papywizard2")
    DATA_STORAGE_DIR = HOME_DIR  # Find a way to retreive the "My Documents" dir in all languages
    TMP_DIR = os.path.expandvars("$TEMP")
else:
    USER_CONFIG_DIR = os.path.join(HOME_DIR, ".config", "papywizard2")  # OpenDesktop standard
    if platform == "maemo":
        DATA_STORAGE_DIR = os.path.join(HOME_DIR, "MyDocs")
    else:
        DATA_STORAGE_DIR = HOME_DIR
    TMP_DIR = "/tmp"
USER_PLUGINS_DIR = os.path.join(USER_CONFIG_DIR, "plugins")
try:
    #os.makedirs(USER_CONFIG_DIR)
    os.makedirs(USER_PLUGINS_DIR)
except OSError, (errno, errmsg):
    if errno in (17, 183):  # dir already exists
        pass
    else:
        raise
CONFIG_FILE = "papywizard.conf"
USER_CONFIG_FILE = os.path.join(USER_CONFIG_DIR, CONFIG_FILE)
PRESET_FILE = "presets.xml"
USER_PRESET_FILE = os.path.join(USER_CONFIG_DIR, PRESET_FILE)
if VERSION_MINOR % 2:
    USER_GUIDE_URL = "http://www.papywizard.org/wiki/UserGuideSvn"
else:
    USER_GUIDE_URL = "http://www.papywizard.org/wiki/UserGuide2.x"
STYLESHEET_FILE = "papywizard.css"
USER_STYLESHEET_FILE = os.path.join(USER_CONFIG_DIR, STYLESHEET_FILE)
SPLASHCREEN_FILE = "splashscreen.png"

# Model
SENSOR_RATIOS = {'3:2': 3./2., '4:3': 4./3., '5:4': 5./4., '16:9': 16./9.}

# View
COLOR_SCHEME = 'default'
ALPHA = 224
SHOOTING_COLOR_SCHEME = {'default': {'background': (224, 224, 224, 255),
                                     'head': (0, 0, 255, 255),
                                     'border': (64, 64, 64, ALPHA),
                                     'preview': (128, 128, 128, ALPHA),
                                     'preview-next': (255, 255, 0, ALPHA),
                                     'preview-toshoot': (160, 160, 160, ALPHA),
                                     'ok': (0, 255, 0, ALPHA),
                                     'ok-next': (255, 255, 0, ALPHA),
                                     'ok-toshoot': (160, 255, 160, ALPHA),
                                     'invalid': (160, 0, 255, ALPHA),
                                     'invalid-next': (255, 255, 0, ALPHA),
                                     'invalid-toshoot': (255, 160, 255, ALPHA),
                                     'error': (255, 0, 0, ALPHA),
                                     'error-next': (255, 255, 0, ALPHA),
                                     'error-toshoot': (255, 160, 160, ALPHA),
                                     },
                         'dark': {'background': (32, 32, 32, 255),
                                  'head': (0, 0, 128, 255),
                                  'border': (160, 160, 160, ALPHA),
                                  'preview': (64, 64, 64, ALPHA),
                                  'preview-next': (128, 128, 0, ALPHA),
                                  'preview-toshoot': (96, 96, 96, ALPHA),
                                  'ok': (0, 128, 0, ALPHA),
                                  'ok-next': (128, 128, 0, ALPHA),
                                  'ok-toshoot': (96, 160, 96, ALPHA),
                                  'invalid': (96, 0, 160, ALPHA),
                                  'invalid-next': (128, 64, 255, ALPHA),
                                  'invalid-toshoot': (128, 96, 0, ALPHA),
                                  'error': (160, 0, 0, ALPHA),
                                  'error-next': (128, 128, 0, ALPHA),
                                  'error-toshoot': (128, 96, 96, ALPHA),
                              }
                        }

# GUI index for controller
HEAD_ORIENTATION_INDEX = {'up': 0, 'left': 1, 'right': 2, 'down': 3,
                          0: 'up', 1: 'left', 2: 'right', 3: 'down'}
PITCH_ARM_SIDE_INDEX = {'right': 0, 'left': 1,
                        0: 'right', 1: 'left'}
CAMERA_ORIENTATION_INDEX = {'portrait': 0, 'landscape': 1, 'custom': 2,
                            0: 'portrait', 1: 'landscape', 2: 'custom'}
MOSAIC_START_FROM_INDEX = {'top-left': 0, 'top-right': 1, 'bottom-left': 2, 'bottom-right': 3, 'nearest-corner': 4,
                           0: 'top-left', 1 : 'top-right', 2: 'bottom-left', 3: 'bottom-right', 4: 'nearest-corner'}
MOSAIC_INITIAL_DIR_INDEX = {'yaw': 0, 'pitch': 1,
                            0: 'yaw', 1: 'pitch'}
SENSOR_RATIO_INDEX = {'3:2': 0, '4:3': 1, '5:4': 2, '16:9': 3,
                      0: '3:2', 1: '4:3', 2: '5:4', 3: '16:9'}
LENS_TYPE_INDEX = {'rectilinear': 0, 'fisheye': 1,
                   0: 'rectilinear', 1: 'fisheye'}
DRIVER_INDEX = {'bluetooth': 0, 'serial': 1, 'ethernet': 2,
                0: 'bluetooth', 1: 'serial', 2: 'ethernet'}
LOGGER_INDEX = {'trace': 0, 'debug': 1, 'info': 2, 'warning' :3, 'error': 4, 'exception': 5, 'critical': 6,
                0: 'trace', 1: 'debug', 2: 'info', 3: 'warning', 4: 'error', 5: 'exception', 6: 'critical'}

# Logger
LOGGER_FORMAT = "%(asctime)s::%(threadName)s::%(levelname)s::%(message)s"
LOGGER_MAX_COUNT_LINE = 1000
LOGGER_FILENAME = "papywizard.log"
LOGGER_MAX_BYTES = 100 * 1024
LOGGER_BACKUP_COUNT = 3

# Hardware
BLUETOOTH_DRIVER_CONNECT_DELAY = 8.

# Spy
SPY_REFRESH_DELAY = 200  # ms

# Low-level simulator
SIMUL_DEFAULT_CONNEXION = 'ethernet'
SIMUL_DEFAULT_SERIAL_PORT = "/dev/ttyS0"
#SIMUL_DEFAULT_SERIAL_PORT = "COM1"
SIMUL_DEFAULT_ETHERNET_HOST = "127.0.0.1"
SIMUL_DEFAULT_ETHERNET_PORT = 7165
SIMUL_DEFAULT_LOGGER_LEVEL = 'debug'
