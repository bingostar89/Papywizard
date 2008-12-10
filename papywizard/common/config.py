# -*- coding: utf-8 -*-

""" Panohead remote control.

License
=======

 - B{papywizard} (U{http://trac.gbiloba.org/papywizard}) is Copyright:
  - (C) 2007-2008 Frédéric Mantegazza

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
@copyright: (C) 2007-2008 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

import sys
import os.path

# Version
VERSION_MAJOR = 1
VERSION_MINOR = 5 # Odd means dev. release
VERSION_UPDATE = 1
VERSION = "%d.%d.%d" % (VERSION_MAJOR, VERSION_MINOR, VERSION_UPDATE)
VERSION_XML = "a"

# Paths
HOME_DIR = os.path.expanduser("~")
if sys.platform == 'win32': # and win64 ?
    USER_CONFIG_DIR = os.path.join(os.path.expandvars("$APPDATA"), "papywizard")
    DATA_STORAGE_DIR = HOME_DIR # Find a way to retreive the "My Documents" dir in all languages
else:
    USER_CONFIG_DIR = os.path.join(HOME_DIR, ".config", "papywizard") # OpenDesktop standard
    try:
        import hildon
        DATA_STORAGE_DIR = os.path.join(HOME_DIR, "MyDocs")
    except ImportError:
        DATA_STORAGE_DIR = HOME_DIR
try:
    os.makedirs(USER_CONFIG_DIR)
except OSError, (errno, errmsg):
    if errno in (17, 183): # dir already exists
        pass
    else:
        raise
CONFIG_FILE = "papywizard.conf"
USER_CONFIG_FILE = os.path.join(USER_CONFIG_DIR, CONFIG_FILE)
PRESET_FILE = "presets.xml"
USER_PRESET_FILE = os.path.join(USER_CONFIG_DIR, PRESET_FILE)
USER_GUIDE_URL = "http://trac.gbiloba.org/papywizard/wiki/UserGuide"
GTKRC_FILE = "gtkrc"
USER_GTKRC_FILE = os.path.join(USER_CONFIG_DIR, GTKRC_FILE)

# GUI index for controller
HEAD_ORIENTATION_INDEX = {'up': 0, 'left': 1, 'right': 2, 'down': 3,
                          0: 'up', 1: 'left', 2: 'right', 3: 'down'}
CAMERA_ORIENTATION_INDEX = {'portrait': 0, 'landscape': 1, 'custom': 2,
                            0: 'portrait', 1: 'landscape', 2: 'custom'}
CAMERA_BRACKETING_INTENT_INDEX = {'exposure': 0, 'focus' : 1, 'white balance': 2, 'movement': 3,
                                  0: 'exposure', 1: 'focus', 2: 'white balance', 3: 'movement'}
LENS_TYPE_INDEX = {'rectilinear': 0, 'fisheye': 1,
                   0: 'rectilinear', 1: 'fisheye'}
MOSAIC_START_FROM_INDEX = {'start': 0, 'end': 1,
                           0: 'start', 1 : 'end'}
MOSAIC_INITIAL_DIR_INDEX = {'yaw': 0, 'pitch': 1,
                            0: 'yaw', 1: 'pitch'}
LOGGER_INDEX = {'trace': 0, 'debug': 1, 'info': 2, 'warning' :3, 'error': 4, 'exception': 5, 'critical': 6,
                0: 'trace', 1: 'debug', 2: 'info', 3: 'warning', 4: 'error', 5: 'exception', 6: 'critical'}
DRIVER_INDEX = {'bluetooth': 0, 'serial': 1, 'ethernet': 2,
                0: 'bluetooth', 1: 'serial', 2: 'ethernet'}
SENSOR_RATIOS_INDEX = {'3:2': 0, '4:3': 1, '5:4': 2,
                       0: '3:2', 1: '4:3', 2: '5:4'}

# Model
SENSOR_RATIOS = {'3:2': 3./2., '4:3': 4./3., '5:4': 5./4.}

# View
SHOOTING_COLOR_SCHEME = {'default': {'background': "#d0d0d0",
                                     'axis': "#ff8080",
                                     'head': "#0000ff",
                                     'border': "#000000",
                                     'border-next': "#ffffff",
                                     'preview': "#c0c0c0",
                                     'skip': "#a0a0a0",
                                     'ok': "#00ff00",
                                     'ok-reshoot': "#c0ffc0",
                                     'error': "#ff0000",
                                     'error-reshoot': "#ffc0c0"
                                    }
                        }

# Logger
LOGGER_FORMAT = "%(asctime)s::%(threadName)s::%(levelname)s::%(message)s"
LOGGER_MAX_COUNT_LINE = 200
LOGGER_FILENAME = "papywizard.log"

# Hardware
AXIS_NUM_YAW = 1
AXIS_NUM_PITCH = 2
AXIS_ACCURACY = 0.1
SHOOT_PULSE = 0.2
BLUETOOTH_DRIVER_CONNECT_DELAY = 8.
ENCODER_360 = 0x0E6600
ENCODER_ZERO = 0x800000
MANUAL_SPEED = {'slow': 170,  # "aa0000"  / 5
                'normal': 34, # "220000"
                'fast':17}    # "110000"  * 2

AXIS_SPEED = 15.
SERIAL_BAUDRATE = 9600
SERIAL_TIMEOUT = 0.2

# Misc
SERIALIZER_REFRESH = 10 # ms
SPY_SLOW_REFRESH = 0.5  # s
SPY_FAST_REFRESH = 0.1  # s

# View3D
VIEW3D_HEAD_HFOV = 30.
VIEW3D_HEAD_VFOV = 20.
VIEW3D_HEAD_FOV_LENGTH = 1.
VIEW3D_LOGGER_LEVEL = 'debug'

# Low-level simulator
SIMUL_DEFAULT_CONNEXION = 'ethernet'
SIMUL_SERIAL_PORT = "/dev/ttyS0"
#SIMUL_SERIAL_PORT = "COM1"
SIMUL_ETHERNET_HOST = "localhost"
SIMUL_ETHERNET_PORT = 7165
SIMUL_LOGGER_LEVEL = 'debug'

# Publisher
PUBLISHER_ENABLE = True
PUBLISHER_HOST = 'localhost'
PUBLISHER_PORT = 7166
