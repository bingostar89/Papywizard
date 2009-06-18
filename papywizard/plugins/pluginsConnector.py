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

Model

Implements
==========

- PluginsConnector
- PluginsConnectorThread

@author: Frédéric Mantegazza
@copyright: (C) 2007-2009 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id: ConnectController.py 1914 2009-06-13 17:50:11Z fma $"

from PyQt4 import QtCore

from papywizard.common.loggingServices import Logger
from papywizard.common.configManager import ConfigManager
from papywizard.plugins.pluginsManager import PluginsManager


class PluginsConnector(QtCore.QObject):
    """
    """
    def __init__(self):
        QtCore.QObject.__init__(self)

        self.__pluginsStatus = {'yawAxis': {'connect': False, 'init': False},
                                'pitchAxis': {'connect': False, 'init': False},
                                'shutter': {'connect': False, 'init': False}
                                }

    # Signals
    def currentStep(self, step):
        """ The connector starts a new step.

        @param step: new current step
        @type step: str
        """
        self.emit(QtCore.SIGNAL("currentStep"), step)

    def stepStatus(self, status):
        """
        """
        self.emit(QtCore.SIGNAL("stepStatus"), status)

    def finished(self):
        """
        """
        self.emit(QtCore.SIGNAL("finished"))

    # Interface
    def start(self):
        """ Start connection.
        """

        # Connect 'yawAxis' plugin
        pluginName = ConfigManager().get('Plugins/PLUGIN_YAW_AXIS')
        plugin = PluginsManager ().get('yawAxis', pluginName)[0]
        self.currentStep(self.tr("'yawAxis' connection..."))
        try:
            plugin.establishConnection()
        except:
            Logger().exception("PluginsConnector.connectPlugins()")
            self.stepStatus('Failed')
        else:
            self.__pluginsStatus['yawAxis']['connect'] = True
            self.stepStatus('Ok')
            self.currentStep(self.tr("'yawAxis' init..."))
            try:
                plugin.init()
            except:
                Logger().exception("PluginsConnector.connectPlugins()")
                self.stepStatus('Failed')
            else:
                self.__pluginsStatus['yawAxis']['init'] = True
                self.stepStatus('Ok')

        # Connect 'pitchAxis' plugin
        pluginName = ConfigManager().get('Plugins/PLUGIN_PITCH_AXIS')
        plugin = PluginsManager ().get('pitchAxis', pluginName)[0]
        self.currentStep(self.tr("'pitchAxis' connection..."))
        try:
            plugin.establishConnection()
        except:
            Logger().exception("PluginsConnector.connectPlugins()")
            self.__pluginsStatus['pitchAxis']['connect'] = False
            self.stepStatus('Failed')
        else:
            self.__pluginsStatus['pitchAxis']['connect'] = True
            self.stepStatus('Ok')
            self.currentStep(self.tr("'pitchAxis' init..."))
            try:
                plugin.init()
            except:
                Logger().exception("PluginsConnector.connectPlugins()")
                self.stepStatus('Failed')
            else:
                self.__pluginsStatus['pitchAxis']['init'] = True
                self.stepStatus('Ok')

        # Connect 'shutter' plugin
        pluginName = ConfigManager().get('Plugins/PLUGIN_SHUTTER')
        plugin = PluginsManager ().get('shutter', pluginName)[0]
        self.currentStep(self.tr("'shutter' connection..."))
        try:
            plugin.establishConnection()
        except:
            Logger().exception("PluginsConnector.connectPlugins()")
            self.stepStatus('Failed')
        else:
            self.__pluginsStatus['shutter']['connect'] = True
            self.stepStatus('Ok')
            self.currentStep(self.tr("'shutter' init..."))
            try:
                plugin.init()
            except:
                Logger().exception("PluginsConnector.connectPlugins()")
                self.stepStatus('Failed')
            else:
                self.__pluginsStatus['shutter']['init'] = True
                self.stepStatus('Ok')

        self.finished()

    def getPluginsStatus(self):
        """ Get the plugins status.

        @return: plugins status
        @rtype: dict
        """
        return self.__pluginsStatus
