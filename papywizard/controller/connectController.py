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

Graphical toolkit controller

Implements
==========

- ConnectController

@author: Frédéric Mantegazza
@copyright: (C) 2007-2009 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id: ConnectController.py 1914 2009-06-13 17:50:11Z fma $"

from PyQt4 import QtCore, QtGui

from papywizard.common.loggingServices import Logger
from papywizard.common.configManager import ConfigManager
from papywizard.plugins.pluginsManager  import PluginsManager
from papywizard.controller.spy import Spy
from papywizard.controller.abstractController import AbstractModalDialogController
from papywizard.view.messageDialog import ExceptionMessageDialog


class ConnectController(AbstractModalDialogController):
    """ Connect controller object.
    """
    def _init(self):
        self._uiFile = "connectDialog.ui"

        self.__plugins = ['yawAxis', 'pitchAxis', 'shutter']

    def _initWidgets(self):
        pass

    def connectToPlugins(self):
        """ Connect to plugins.

        @return: plugins connection status
        @rtype: dict
        """
        Logger().info("Connecting...")

        pluginsStatus = {'yawAxis': {'connect': False, 'init': False},
                         'pitchAxis': {'connect': False, 'init': False},
                         'shutter': {'connect': False, 'init': False}
                         }

        # Wait cursor
        self._view.setCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))

        # Connect 'yawAxis' plugin
        pluginName = ConfigManager().get('Plugins/PLUGIN_YAW_AXIS')
        plugin = PluginsManager ().get('yawAxis', pluginName)[0]
        item = QtGui.QListWidgetItem("'yawAxis' establish connection...")
        self._view.pluginsStatusListWidget.addItem(item)
        for i in xrange(5000):
            QtGui.QApplication.processEvents(QtCore.QEventLoop.ExcludeUserInputEvents)
        try:
            plugin.establishConnection()
        except:
            Logger().exception("MainController.__connect()")
            item.setText(item.text() + "  Failed")
            item.setTextColor(QtGui.QColor("red"))
            for i in xrange(5000):
                QtGui.QApplication.processEvents(QtCore.QEventLoop.ExcludeUserInputEvents)
        else:
            item.setText(item.text()  + "  Ok")
            item.setTextColor(QtGui.QColor("green"))
            pluginsStatus['yawAxis']['connect'] = True
            item = QtGui.QListWidgetItem("'yawAxis' init...")
            self._view.pluginsStatusListWidget.addItem(item)
            for i in xrange(5000):
                QtGui.QApplication.processEvents(QtCore.QEventLoop.ExcludeUserInputEvents)
            try:
                plugin.init()
            except:
                Logger().exception("MainController.__connect()")
                item.setText(item.text() + "  Failed")
                item.setTextColor(QtGui.QColor("red"))
                for i in xrange(5000):
                    QtGui.QApplication.processEvents(QtCore.QEventLoop.ExcludeUserInputEvents)
            else:
                item.setText(item.text() + "  Ok")
                item.setTextColor(QtGui.QColor("green"))
                for i in xrange(5000):
                    QtGui.QApplication.processEvents(QtCore.QEventLoop.ExcludeUserInputEvents)
                pluginsStatus['yawAxis']['init'] = True

        # Connect 'pitchAxis' plugin
        pluginName = ConfigManager().get('Plugins/PLUGIN_PITCH_AXIS')
        plugin = PluginsManager ().get('pitchAxis', pluginName)[0]
        item = QtGui.QListWidgetItem("'pitchAxis' establish connection...")
        self._view.pluginsStatusListWidget.addItem(item)
        for i in xrange(5000):
            QtGui.QApplication.processEvents(QtCore.QEventLoop.ExcludeUserInputEvents)
        try:
            plugin.establishConnection()
        except:
            Logger().exception("MainController.__connect()")
            item.setText(item.text() + "  Failed")
            item.setTextColor(QtGui.QColor("red"))
            for i in xrange(5000):
                QtGui.QApplication.processEvents(QtCore.QEventLoop.ExcludeUserInputEvents)
        else:
            item.setText(item.text() + "  Ok")
            item.setTextColor(QtGui.QColor("green"))
            pluginsStatus['pitchAxis']['connect'] = True
            item = QtGui.QListWidgetItem("'pitchAxis' init...")
            self._view.pluginsStatusListWidget.addItem(item)
            for i in xrange(5000):
                QtGui.QApplication.processEvents(QtCore.QEventLoop.ExcludeUserInputEvents)
            try:
                plugin.init()
            except:
                Logger().exception("MainController.__connect()")
                item.setText(item.text() + "  Failed")
                item.setTextColor(QtGui.QColor("red"))
                for i in xrange(5000):
                    QtGui.QApplication.processEvents(QtCore.QEventLoop.ExcludeUserInputEvents)
            else:
                item.setText(item.text() + "  Ok")
                item.setTextColor(QtGui.QColor("green"))
                for i in xrange(5000):
                    QtGui.QApplication.processEvents(QtCore.QEventLoop.ExcludeUserInputEvents)
                pluginsStatus['pitchAxis']['init'] = True

        # Connect 'shutter' plugin
        pluginName = ConfigManager().get('Plugins/PLUGIN_SHUTTER')
        plugin = PluginsManager ().get('shutter', pluginName)[0]
        item = QtGui.QListWidgetItem("'shutter' establish connection...")
        self._view.pluginsStatusListWidget.addItem(item)
        for i in xrange(5000):
            QtGui.QApplication.processEvents(QtCore.QEventLoop.ExcludeUserInputEvents)
        try:
            plugin.establishConnection()
        except:
            Logger().exception("MainController.__connect()")
            item.setText(item.text() + "  Failed")
            item.setTextColor(QtGui.QColor("red"))
            for i in xrange(5000):
                QtGui.QApplication.processEvents(QtCore.QEventLoop.ExcludeUserInputEvents)
        else:
            item.setTextColor(QtGui.QColor("green"))
            item.setText(item.text() + "  Ok")
            pluginsStatus['shutter']['connect'] = True
            item = QtGui.QListWidgetItem("'shutter' init...")
            self._view.pluginsStatusListWidget.addItem(item)
            for i in xrange(5000):
                QtGui.QApplication.processEvents(QtCore.QEventLoop.ExcludeUserInputEvents)
            try:
                plugin.init()
            except:
                Logger().exception("MainController.__connect()")
                item.setText(item.text() + "  Failed")
                item.setTextColor(QtGui.QColor("red"))
                for i in xrange(5000):
                    QtGui.QApplication.processEvents(QtCore.QEventLoop.ExcludeUserInputEvents)
            else:
                item.setText(item.text() + "  Ok")
                item.setTextColor(QtGui.QColor("green"))
                for i in xrange(5000):
                    QtGui.QApplication.processEvents(QtCore.QEventLoop.ExcludeUserInputEvents)
                pluginsStatus['shutter']['init'] = True

        # Restore cursor and buttons
        self._view.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self._view.buttonBox.setEnabled(True)

        return pluginsStatus

    def disconnectFromPlugins(self, pluginStatus):
        """ Disconnect from plugins.

        @param pluginsStatus: plugins connection status
        @type pluginsStatus: dict
        """
        Logger().info("Disconnecting...")

        Spy().suspend()

        # Wait cursor
        self._view.setCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))

        # Disconnect 'yawAxis' plugin
        pluginName = ConfigManager().get('Plugins/PLUGIN_YAW_AXIS')
        plugin = PluginsManager ().get('yawAxis', pluginName)[0]
        if pluginsStatus['yawAxis']['init']:
            try:
                plugin.shutdown()
            except:
                Logger().exception("MainController.__disconnect()")
            else:
                pluginsStatus['yawAxis']['init'] = False
        if pluginsStatus['yawAxis']['connect']:
            try:
                plugin.stopConnection()
            except:
                Logger().exception("MainController.__disconnect()")
            else:
                pluginsStatus['yawAxis']['connect'] = False
        
        # Disconnect 'pitchAxis' plugin
        pluginName = ConfigManager().get('Plugins/PLUGIN_PITCH_AXIS')
        plugin = PluginsManager ().get('pitchAxis', pluginName)[0]
        if pluginsStatus['pitchAxis']['init']:
            try:
                plugin.shutdown()
            except:
                Logger().exception("MainController.__disconnect()")
            else:
                pluginsStatus['pitchAxis']['init'] = False
        if pluginsStatus['pitchAxis']['connect']:
            try:
                plugin.stopConnection()
            except:
                Logger().exception("MainController.__disconnect()")
            else:
                pluginsStatus['pitchAxis']['connect'] = False

        # Disconnect 'shutter' plugin
        pluginName = ConfigManager().get('Plugins/PLUGIN_SHUTTER')
        plugin = PluginsManager ().get('shutter', pluginName)[0]
        if pluginsStatus['shutter']['init']:
            try:
                plugin.shutdown()
            except:
                Logger().exception("MainController.__disconnect()")
            else:
                pluginsStatus['shutter']['init'] = False
        if pluginsStatus['shutter']['connect']:
            try:
                plugin.stopConnection()
            except:
                Logger().exception("MainController.__disconnect()")
            else:
                pluginsStatus['shutter']['connect'] = False

        # Restore cursor
        self._view.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))

        # Check disconnection status
        if not pluginsStatus['yawAxis']['connect'] and \
           not pluginsStatus['pitchAxis']['connect'] and \
           not pluginsStatus['shutter']['connect']:
            Logger().info("Disconnected")
            return True
        else:
            Logger().error("Disconnection failed")
            return False

    # Interface
    def refreshView(self):
        pass
