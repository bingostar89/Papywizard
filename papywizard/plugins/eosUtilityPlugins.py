# -*- coding: utf-8 -*-

""" Panohead remote control.

License
=======

 - B{papywizard} (U{http://trac.gbiloba.org/papywizard}) is Copyright:
  - (C) 2007-2009 Frédéric Mantegazza

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

Plugins

Implements
==========

- EOSUtilityShutter
- EOSUtilityShutterController

@author: Jones Henry Subbiah
@author: Frédéric Mantegazza
@copyright: (C) 2009 Jones Henry Subbiah
@copyright: (C) 2007-2009 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

import time
import subprocess

from papywizard.common.loggingServices import Logger
from papywizard.common.pluginManager import PluginManager
from papywizard.hardware.abstractShutterPlugin import AbstractShutterPlugin
from papywizard.controller.shutterPluginController import ShutterPluginController
from papywizard.view.pluginFields import ComboBoxField, LineEditField, SpinBoxField, CheckBoxField

DEFAULT_PROGRAM_PATH = "C:\\Program Files\\Papywizard\\EOSBracket.exe"
DEFAULT_EOSUTILITY_TYPE = 'new'
DEFAULT_EXPOSURE_BRACKETING_STOPS = '1'
DEFAULT_EXPOSURE_BRACKETING_TYPE = '0-+'
DEFAULT_EXPOSURE_BRACKETING_NBPICTS = 1
DEFAULT_SHOOT_PICTURES = False
DEFAULT_BULB_MODE = False
DEFAULT_BASE_BULB_EXPOSURE = 1
DEFAULT_FOCUS_MODE = False
DEFAULT_FOCUS_DIRECTION = 'far'
DEFAULT_FOCUS_STEP = 'medium'
DEFAULT_FOCUS_STEP_COUNT = 1
DEFAULT_FOCUS_BRACKETING_NBPICTS = 1
EXPOSURE_BRACKETING_TYPE_INDEX = {'0--': '1',
                                  '0++': '2',
                                  '0-+': '3'}


class EOSUtilityShutter(AbstractShutterPlugin):
    _name = "EOS Utility"

    def _init(self):
        pass

    def _getTimeValue(self):
        return -1

    def _getMirrorLockup(self):
        return False

    def _getBracketingNbPicts(self):
        return 1

    def _getBracketingIntent(self):
        return 'exposure'

    def _defineConfig(self):
        #AbstractShutterPlugin._defineConfig(self)
        self._addConfigKey('_eosBracketPath', 'PROGRAM_PATH', default=DEFAULT_PROGRAM_PATH)
        self._addConfigKey('_eosUtilityType', 'EOSUTILITY_TYPE', default=DEFAULT_EOSUTILITY_TYPE)
        self._addConfigKey('_exposureBracketingStops', 'EXPOSURE_BRACKETING_STOPS', default=DEFAULT_EXPOSURE_BRACKETING_STOPS)
        self._addConfigKey('_exposureBracketingType', 'EXPOSURE_BRACKETING_TYPE', default=DEFAULT_EXPOSURE_BRACKETING_TYPE)
        self._addConfigKey('_exposureBracketingNbPicts', 'EXPOSURE_BRACKETING_NBPICTS', default=DEFAULT_EXPOSURE_BRACKETING_NBPICTS)
        self._addConfigKey('_shootPictures', 'SHOOT_PICTURES', default=DEFAULT_SHOOT_PICTURES)
        self._addConfigKey('_bulbMode', 'BULB_MODE', default=DEFAULT_BULB_MODE)
        self._addConfigKey('_baseBulbExposure', 'BASE_BULB_EXPOSURE', default=DEFAULT_BASE_BULB_EXPOSURE)
        self._addConfigKey('_focusBracketMode', 'FOCUS_MODE', default=DEFAULT_FOCUS_MODE)
        self._addConfigKey('_focusDirection', 'FOCUS_DIRECTION', default=DEFAULT_FOCUS_DIRECTION)
        self._addConfigKey('_focusStep', 'FOCUS_STEP', default=DEFAULT_FOCUS_STEP)
        self._addConfigKey('_focusStepCount', 'FOCUS_STEP_COUNT', default=DEFAULT_FOCUS_STEP_COUNT)
        self._addConfigKey('_focusBracketingNbPictures', 'FOCUS_BRACKETING_NBPICTS', default=DEFAULT_FOCUS_BRACKETING_NBPICTS)

    def activate(self):
        Logger().trace("EOSUtilityShutter.activate()")

    def shutdown(self):
        Logger().trace("EOSUtilityShutter.shutdown()")

    def establishConnection(self):
        pass

    def shutdownConnection(self):
        pass

    def lockupMirror(self):
        Logger().debug("EOSUtilityShutter.lockupMirror(): Not possible with EOS Utility")
        return 0

    def shoot(self, bracketNumber):
        Logger().debug("EOSUtilityShutter.shoot(): EOSBracket Path '%s'..." % self._config['PROGRAM_PATH'])
        Logger().debug("EOSUtilityShutter.shoot(): EOS Utility Type '%s'..." % self._config['EOSUTILITY_TYPE'])
        Logger().debug("EOSUtilityShutter.shoot(): Exposure Bracketing Stops '%s'..." % self._config['EXPOSURE_BRACKETING_STOPS'])
        Logger().debug("EOSUtilityShutter.shoot(): Exposure Bracketing Type '%s'..." % self._config['EXPOSURE_BRACKETING_TYPE'])
        Logger().debug("EOSUtilityShutter.shoot(): Exposure Bracketing NB Pictures '%s'..." % self._config['EXPOSURE_BRACKETING_NBPICTS'])
        Logger().debug("EOSUtilityShutter.shoot(): Shoot Pictures? '%s'..." % self._config['SHOOT_PICTURES'])
        Logger().debug("EOSUtilityShutter.shoot(): Bulb Mode? '%s'..." % self._config['BULB_MODE'])
        Logger().debug("EOSUtilityShutter.shoot(): Base Bulb Exposure (in secs) '%s'..." % self._config['BASE_BULB_EXPOSURE'])
        Logger().debug("EOSUtilityShutter.shoot(): Focus Bracket Mode '%s'..." % self._config['FOCUS_MODE'])
        Logger().debug("EOSUtilityShutter.shoot(): Focus Direction '%s'..." % self._config['FOCUS_DIRECTION'])
        Logger().debug("EOSUtilityShutter.shoot(): Focus Step Mode '%s'..." % self._config['FOCUS_STEP'])
        Logger().debug("EOSUtilityShutter.shoot(): Focus Step Count '%s'..." % self._config['FOCUS_STEP_COUNT'])
        Logger().debug("EOSUtilityShutter.shoot(): Focus Bracketing NB Pictures '%s'..." % self._config['FOCUS_BRACKETING_NBPICTS'])

        args = []
        args.append(self._config['PROGRAM_PATH'])
        args.append("CL")
        args.append(self._config['EOSUTILITY_TYPE'])
        args.append(self._config['EXPOSURE_BRACKETING_STOPS'])
        args.append(EXPOSURE_BRACKETING_TYPE_INDEX[self._config['EXPOSURE_BRACKETING_TYPE']])
        args.append(str(self._config['EXPOSURE_BRACKETING_NBPICTS']))
        if self._config['SHOOT_PICTURES']:
            args.append("y")
        else:
            args.append("N")
        if self._config['BULB_MODE']:
            args.append("y")
        else:
            args.append("n")
        args.append(str(self._config['BASE_BULB_EXPOSURE']))
        if self._config['FOCUS_MODE']:
            args.append("y")
        else:
            args.append("n")
        args.append(self._config['FOCUS_DIRECTION'])
        args.append(self._config['FOCUS_STEP'])
        args.append(str(self._config['FOCUS_STEP_COUNT']))
        args.append(str(self._config['FOCUS_BRACKETING_NBPICTS']))
        Logger().debug("EOSUtilityShutter.shoot(): cmdLineArgs '%s'..." % ' '.join(args))

        # Launch external command
        p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Wait end of execution
        stdout, stderr = p.communicate()
        if stderr:
            Logger().debug("EOSUtilityShutter.shoot(): stderr:\n%s" % stderr)
        Logger().debug("EOSUtilityShutter.shoot(): stdout:\n%s" % stdout)

        return p.returncode


class EOSUtilityShutterController(ShutterPluginController):
    def _defineGui(self):
        #ShutterPluginController._defineGui(self)
        self._addWidget('Main', "EOS Bracket path", LineEditField, (), 'PROGRAM_PATH')
        self._addWidget('Main', "EOS Utility Type", ComboBoxField, (['old', 'new'],), 'EOSUTILITY_TYPE')
        self._addWidget('Main', "Exposure Bracketing Stops", ComboBoxField, (['1/3', '2/3', '1', '1 1/3', '1 2/3', '2', '2 1/3', '2 2/3', '3', '3 1/3', '3 2/3', '4', '4 1/3', '4 2/3', '5', '5 1/3', '5 2/3', '6'],), 'EXPOSURE_BRACKETING_STOPS')
        self._addWidget('Main', "Exposure Bracketing Type", ComboBoxField, (EXPOSURE_BRACKETING_TYPE_INDEX.keys(),), 'EXPOSURE_BRACKETING_TYPE')
        self._addWidget('Main', "Exposure Bracketing Picture Count", SpinBoxField, (1, 99), 'EXPOSURE_BRACKETING_NBPICTS')
        self._addWidget('Main', "Shoot Pictures", CheckBoxField, (), 'SHOOT_PICTURES')
        self._addTab('Bulb')
        self._addWidget('Bulb', "Bulb Exposure Mode", CheckBoxField, (), 'BULB_MODE')
        self._addWidget('Bulb', "Base Bulb Exposure", SpinBoxField, (1, 99, "", " s"), 'BASE_BULB_EXPOSURE')
        self._addTab('Focus')
        self._addWidget('Focus', "Focus Bracket Mode", CheckBoxField, (), 'FOCUS_MODE')
        self._addWidget('Focus', "Focus Direction", ComboBoxField, (['far', 'near'],), 'FOCUS_DIRECTION')
        self._addWidget('Focus', "Focus Step Mode", ComboBoxField, (['small', 'medium', 'large'],), 'FOCUS_STEP')
        self._addWidget('Focus', "Focus Step Count", SpinBoxField, (1, 99), 'FOCUS_STEP_COUNT')
        self._addWidget('Focus', "Focus Bracketing Picture Count", SpinBoxField, (1, 99), 'FOCUS_BRACKETING_NBPICTS')

def register():
    """ Register plugins.
    """
    PluginManager().register(EOSUtilityShutter, EOSUtilityShutterController)
