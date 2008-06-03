# -*- coding: iso-8859-1 -*-

""" Panohead remote control.

Configurations.

@author: Frederic Mantegazza
@copyright: 2007
@license: CeCILL
@todo:
"""

__revision__ = "$Id$"

import sys
import os.path
import logging


VERSION = "0.9beta2"

# General config
if sys.platform.startswith("linux") or sys.platform.startswith("Mac"):
    HOME_DIR = os.path.expandvars("$HOME")
    CONFIG_DIR = os.path.join(HOME_DIR, ".papywizard")
    try:
        os.mkdir(CONFIG_DIR)
    except OSError, (errno, errmsg):
        if errno == 17:
            pass
        else:
            raise
    TEMP_DIR = "/tmp"
elif sys.platform.startswith("win"):
    import win32api
    HOME_DIR = win32api.ExpandEnvironmentStrings("%HOMEPATH%")
    CONFIG_DIR = os.path.join(HOME_DIR, ".papywizard")
    try:
        os.mkdir(CONFIG_DIR)
    except OSError, (errno, errmsg):
        if errno == 183:
            pass
        else:
            raise
    TEMP_DIR = CONFIG_DIR

# Hardware configuration
AXIS_NUM_YAW = 1
AXIS_NUM_PITCH = 2
AXIS_ACCURACY = 0.1          # (°)
SHOOT_PULSE = 0.2            # (s)

AXIS_SPEED = 10.             # used in simulation (°/s)

DRIVER = "bluetooth"         # Driver to use, in ('serialPasive', 'serialStamp', 'bluetooth')
BLUETOOTH_DEVICE_ADDRESS = "00:50:C2:58:55:B9"
BLUETOOTH_DRIVER_CONNECT_DELAY = 8
SERIAL_PORT = 0              # O is first COM port, 1 is second...
SERIAL_BAUDRATE = 9600
SERIAL_TIMEOUT = .2          # (s)

ENCODER_360 = 0x0E6600
ENCODER_ZERO = 0x800000

# Model configuration
CONFIG_FILE = os.path.join(CONFIG_DIR, "papywizardrc")
DATA_FILE = os.path.join(HOME_DIR, "papywizard-%s.xml")
SENSOR_RATIOS = {'3:2':3./2., '4:3':4./3.}
SENSOR_RATIOS_INDEX = {'3:2':0, '4:3':1,
                       0:'3:2', 1:'4:3'} # for pygtk
DEFAULT_SENSOR_RATIO = "3:2"
CAMERA_ORIENTATION_INDEX = {'portrait':0, 'landscape':1,
                            0:'portrait', 1:'landscape'} # for pygtk
MOSAIC_TEMPLATE = ["Auto",
                   "RDL", "RDR", "RUL", "RDR",
                   "LDR", "LDL", "LUR", "LUL",
                   "DRU", "DRD", "DLU", "DLD",
                   "URD", "URU", "ULD", "ULU"
                   ]
DEFAULT_PREFS = {'shooting': {'overlap': 0.25,
                              'cameraOrientation': 'portrait',
                              'manualShoot': False,
                              'delay': 0.5
                             },
                 'mosaic': {'template': "Auto",
                           },
                 'camera': {'sensorCoef': 1.6,
                            'sensorRatio': DEFAULT_SENSOR_RATIO,
                            'timeValue': 0.5,
                            'nbPicts': 1
                           },
                 'lens': {'focal': 17.0,
                          'fisheye': False
                         }
                }
WRITE_DATA_FILE = False

# Logger configuration
LOGGER_LEVEL = 'trace'
#LOGGER_FORMAT = "%(asctime)s::%(threadName)s::%(levelname)s::%(message)s"
LOGGER_FORMAT = "%(asctime)s::%(levelname)s::%(message)s"
LOGGER_FILENAME = os.path.join(TEMP_DIR, "papywizard.log")
LOGGER_MAXBYTES = 1024 * 1024 # 1MB per file
LOGGER_BACKUPCOUNT = 10 # 10 files max
LOGGER_CONSOLE = True
LOGGER_FILE = True

# 3D view configuration
VIEW3D_ENABLE = False
VIEW3D_HEAD_HFOV = 30
VIEW3D_HEAD_VFOV = 20
VIEW3D_HEAD_FOV_LENGTH = 1

# Misc
SPY_SLOW_REFRESH = 0.5
SPY_FAST_REFRESH = 0.05
