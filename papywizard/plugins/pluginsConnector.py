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

__revision__ = "$Id$"

from PyQt4 import QtCore

from papywizard.common.loggingServices import Logger
from papywizard.common.configManager import ConfigManager
from papywizard.plugins.pluginsManager import PluginsManager


class PluginsConnector(QtCore.QObject):
    """
    """
    def __init__(self):
        QtCore.QObject.__init__(self)

    # Interface
    def start(self):
        """ Start connection.
        """
        pluginsStatus = {'yawAxis': {'connect': False, 'init': False},
                         'pitchAxis': {'connect': False, 'init': False},
                         'shutter': {'connect': False, 'init': False}
                         }

        # Start 'yawAxis' plugin connection
        pluginName = ConfigManager().get('Plugins/PLUGIN_YAW_AXIS')
        plugin = PluginsManager ().get('yawAxis', pluginName)[0]
        Logger().debug("PluginsConnector.start(): 'yawAxis' establish connection")
        try:
            plugin.establishConnection()
        except:
            Logger().exception("PluginsConnector.connectPlugins()")
        else:
            pluginsStatus['yawAxis']['connect'] = True
            Logger().debug("PluginsConnector.start(): 'yawAxis' init")
            try:
                plugin.init()
            except:
                Logger().exception("PluginsConnector.connectPlugins()")
            else:
                pluginsStatus['yawAxis']['init'] = True

        # Start 'pitchAxis' plugin connection
        pluginName = ConfigManager().get('Plugins/PLUGIN_PITCH_AXIS')
        plugin = PluginsManager ().get('pitchAxis', pluginName)[0]
        Logger().debug("PluginsConnector.start(): 'pitchAxis' establish connection")
        try:
            plugin.establishConnection()
        except:
            Logger().exception("PluginsConnector.connectPlugins()")
            pluginsStatus['pitchAxis']['connect'] = False
        else:
            pluginsStatus['pitchAxis']['connect'] = True
            Logger().debug("PluginsConnector.start(): 'pitchAxis' init")
            try:
                plugin.init()
            except:
                Logger().exception("PluginsConnector.connectPlugins()")
            else:
                pluginsStatus['pitchAxis']['init'] = True

        # Start 'shutter' plugin connection
        pluginName = ConfigManager().get('Plugins/PLUGIN_SHUTTER')
        plugin = PluginsManager ().get('shutter', pluginName)[0]
        Logger().debug("PluginsConnector.start(): 'shutter' establish connection")
        try:
            plugin.establishConnection()
        except:
            Logger().exception("PluginsConnector.connectPlugins()")
        else:
            pluginsStatus['shutter']['connect'] = True
            Logger().debug("PluginsConnector.start(): 'shutter' init")
            try:
                plugin.init()
            except:
                Logger().exception("PluginsConnector.connectPlugins()")
            else:
                pluginsStatus['shutter']['init'] = True
                
        return pluginsStatus

    def stop(self, pluginsStatus):
        """ Stop connection.
        """

        # Stop 'yawAxis' plugin connection
        pluginName = ConfigManager().get('Plugins/PLUGIN_YAW_AXIS')
        plugin = PluginsManager ().get('yawAxis', pluginName)[0]
        if pluginsStatus['yawAxis']['init']:
            Logger().debug("PluginsConnector.start(): 'yawAxis' shutdown")
            try:
                plugin.shutdown()
            except:
                Logger().exception("MainController.__stopConnection()")
            else:
                pluginsStatus['yawAxis']['init'] = False
        if pluginsStatus['yawAxis']['connect']:
            Logger().debug("PluginsConnector.start(): 'yawAxis' stop connection")
            try:
                plugin.stopConnection()
            except:
                Logger().exception("MainController.__stopConnection()")
            else:
                pluginsStatus['yawAxis']['connect'] = False

        # Stop 'pitchAxis' plugin connection
        pluginName = ConfigManager().get('Plugins/PLUGIN_PITCH_AXIS')
        plugin = PluginsManager ().get('pitchAxis', pluginName)[0]
        if pluginsStatus['pitchAxis']['init']:
            Logger().debug("PluginsConnector.start(): 'pitchAxis' shutdown")
            try:
                plugin.shutdown()
            except:
                Logger().exception("MainController.__stopConnection()")
            else:
                pluginsStatus['pitchAxis']['init'] = False
        if pluginsStatus['pitchAxis']['connect']:
            Logger().debug("PluginsConnector.start(): 'pitchAxis' stop connection")
            try:
                plugin.stopConnection()
            except:
                Logger().exception("MainController.__stopConnection()")
            else:
                pluginsStatus['pitchAxis']['connect'] = False

        # Stop 'shutter' plugin connection
        pluginName = ConfigManager().get('Plugins/PLUGIN_SHUTTER')
        plugin = PluginsManager ().get('shutter', pluginName)[0]
        if pluginsStatus['shutter']['init']:
            Logger().debug("PluginsConnector.start(): 'shutter' shutdown")
            try:
                plugin.shutdown()
            except:
                Logger().exception("MainController.__stopConnection()")
            else:
                pluginsStatus['shutter']['init'] = False
        if pluginsStatus['shutter']['connect']:
            Logger().debug("PluginsConnector.start(): 'shutter' stop connection")
            try:
                plugin.stopConnection()
            except:
                Logger().exception("MainController.__stopConnection()")
            else:
                pluginsStatus['shutter']['connect'] = False

        return pluginsStatus
