# -*- coding: iso-8859-1 -*-

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

VERSION = "0.99"
PACKAGE_VERSION = 1

HOME_DIR = os.path.expanduser("~")
if sys.platform == 'win32': # and win64 ?
    USER_CONFIG_DIR = os.path.join(os.path.expandvars("$APPDATA"), "papywizard")
else:
    USER_CONFIG_DIR = os.path.join(HOME_DIR, ".config", "papywizard") # OpenDesktop standard
USER_PRESET_DIR = os.path.join(USER_CONFIG_DIR, "presets")
try:
    os.makedirs(USER_PRESET_DIR)
except OSError, (errno, errmsg):
    if errno in (17, 183): # dir already exists
        pass
    else:
        raise
CONFIG_FILE = "papywizard.conf"
USER_CONFIG_FILE = os.path.join(USER_CONFIG_DIR, CONFIG_FILE)

SENSOR_RATIOS = {'3:2': 3./2., '4:3': 4./3.}
SENSOR_RATIOS_INDEX = {'3:2': 0, '4:3': 1, '5:4': 5./4.,
                       0: '3:2', 1: '4:3', 2: '5:4'}

CAMERA_ORIENTATION_INDEX = {'portrait': 0, 'landscape': 1,
                            0: 'portrait', 1: 'landscape'}

MOSAIC_START_FROM_INDEX = {'start': 0, 'end': 1,
                           0: 'start', 1 : 'end'}

MOSAIC_INITIAL_DIR_INDEX = {'yaw': 0, 'pitch': 1,
                            0: 'yaw', 1: 'pitch'}

PRESET_INDEX = {'4@0 + Z + N': 0,
                '3@-15 + Z': 1,
                '6@-15 + 6@30 + N': 2,
                '3 + 6 + 12 + 6 + 3 (28mm)': 3,
                0: '4@0 + Z + N',
                1: '3@-15 + Z',
                2: '6@-15 + 6@30 + N',
                3: '3 + 6 + 12 + 6 + 3 (28mm)'}

PRESET = {'4@0 + Z + N': [(  0.,   0.), (90., 0.), (180., 0.), (270., 0),
                          (270.,  90.),
                          (270., -90.)],
          '3@-15 + Z': [(  0., -15.), (120., -15.), (240., -15.),
                        (240.,  90.)],
          '6@-15 + 6@30 + N': [(  0., -15.), ( 60., -15.), (120., -15.), (180., -15.), (240., -15.), (300., -15.),
                               (300.,  30.), (240.,  30.), (180.,  30.), (120.,  30.), ( 60.,  30.), (  0.,  30.),
                               (  0., -90.)],
          '3 + 6 + 12 + 6 + 3 (28mm)': [(30.,  70.), (150.,  70.), (270.,  70.),
                                        ( 0.,  40.), ( 60.,  40.), (120.,  40.), (180.,  40), (240.,  40.), (300.,  40.),
                                        ( 0.,  10.), ( 30., -10.), ( 60.,  10.), ( 90., -10), (120.,  10.), (150., -10.), (180., 10), (210., -10.), (240., 10.), (270., -10), (300., 10.), (330., -10.),
                                        ( 0., -40.), ( 60., -40.), (120., -40.), (180., -40), (240., -40.), (300., -40.),
                                        (30., -70.), (150., -70.), (270., -70.)]}

# Logger
LOGGER_FORMAT = "%(asctime)s::%(threadName)s::%(levelname)s::%(message)s"
LOGGER_INDEX = {'trace': 0, 'debug': 1, 'info': 2, 'warning' :3, 'error': 4, 'exception': 5, 'critical': 6,
                0: 'trace', 1: 'debug', 2: 'info', 3: 'warning', 4: 'error', 5: 'exception', 6: 'critical'}

# Hardware
AXIS_NUM_YAW = 1
AXIS_NUM_PITCH = 2
AXIS_ACCURACY = 0.1
SHOOT_PULSE = 0.2
BLUETOOTH_DRIVER_CONNECT_DELAY = 8.
ENCODER_360 = 0x0E6600
ENCODER_ZERO = 0x800000
AXIS_SPEED = 15.
SERIAL_BAUDRATE = 9600
SERIAL_TIMEOUT = 0.2
DRIVER_INDEX = {'bluetooth': 0, 'serial': 1, 'usb': 2,
                0: 'bluetooth', 1: 'serial', 2: 'usb'}

# Misc
SPY_SLOW_REFRESH = 0.5
SPY_FAST_REFRESH = 0.05

# View3D
VIEW3D_ENABLE = False
VIEW3D_HEAD_HFOV = 30.
VIEW3D_HEAD_VFOV = 20.
VIEW3D_HEAD_FOV_LENGTH = 1.
