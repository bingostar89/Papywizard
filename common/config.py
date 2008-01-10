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


VERSION = "0.9 beta 1"

# General config
if sys.platform.startswith("linux"):
    TEMP_DIR = "/tmp"
    HOME_DIR = os.path.expandvars("$HOME")
    if HOME_DIR == "$HOME":
        HOME_DIR = TEMP_DIR
elif sys.platform.startswith("win"):
    TEMP_DIR = "C:\\Windows\\Temp"
    HOME_DIR = TEMP_DIR # Find a way to retreive correct home dir
elif sys.platform.startswith("Mac"): # ???
    TEMP_DIR = "/tmp"
    HOME_DIR = os.path.expandvars("$HOME")

# Hardware config
AXIS_NUM_YAW = 1
AXIS_NUM_PITCH = 2
AXIS_ACCURACY = 0.1
SHOOT_PULSE = 0.2

AXIS_SPEED = 10. # mainly for simulation (°/s)

SERIAL_PORT = 0
SERIAL_BAUDRATE = 9600
SERIAL_TIMEOUT = .2

ENCODER_360 = 0x0E6600
ENCODER_ZERO = 0x800000

DRIVER = "serialPassive"

# Model configuration
CONFIG_FILE = os.path.join(HOME_DIR, ".panoheadrc")
SENSOR_RATIOS = {'3:2':3./2., '4:3':4./3.}
DEFAULT_SENSOR_RATIO = "3:2"
MOSAIC_TEMPLATE = ["Auto",
                   "RDL", "RDR", "RUL", "RDR",
                   "LDR", "LDL", "LUR", "LUL",
                   "DRU", "DRD", "DLU", "DLD",
                   "URD", "URU", "ULD", "ULU"
                   ]
DEFAULT_PREFS = {'shooting': {'overlap': 0.25,
                              'cameraOrientation': 'portrait',
                              'manualShoot': False,
                              'delay': 0.0
                             },
                 'mosaic': {'template': "Auto",
                            'zenith': False,
                            'nadir': False
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

# Logger configuration
LOGGER_LEVEL = 'trace'
#LOGGER_FORMAT = "%(asctime)s::%(threadName)s::%(levelname)s::%(message)s"
LOGGER_FORMAT = "%(asctime)s::%(levelname)s::%(message)s"
LOGGER_FILENAME = os.path.join(TEMP_DIR, "panohead.log")
LOGGER_MAXBYTES = 1024 * 1024
LOGGER_BACKUPCOUNT = 10
LOGGER_CONSOLE = True
LOGGER_FILE = True

# 3D simulation configuration
VIEW3D_ENABLE = True
VIEW3D_HEAD_HFOV = 30
VIEW3D_HEAD_VFOV = 20
VIEW3D_HEAD_FOV_LENGTH = 1

# Misc
SPY_SLOW_REFRESH = 0.5
SPY_FAST_REFRESH = 0.05
