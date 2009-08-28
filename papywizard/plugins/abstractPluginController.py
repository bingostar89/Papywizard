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

Plugins architecture

Implements
==========

- AbstractPluginController

@author: Frédéric Mantegazza
@copyright: (C) 2007-2009 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

from PyQt4 import QtCore, QtGui

from papywizard.common.orderedDict import OrderedDict
from papywizard.common.loggingServices import Logger
from papywizard.common.configManager import ConfigManager
from papywizard.controller.abstractController import AbstractModalDialogController


class AbstractPluginController(AbstractModalDialogController):
    """ Plugin controller.

    Used for the configuration dialog of the plugin.
    The dialog is mainly a tab widget where all options
    of the plugin are listed, as name/widget list.
    """
    def _init(self):
        self._uiFile = "pluginsConfigDialog.ui"
        self._fields = OrderedDict()

        # Add a general tab
        self._addTab('Main')

    def _addTab(self, tabName):
        """ Add a new tab to the tab widget.

        @param tabName: name of the new tab
        @type tabName: str
        """
        self._fields[tabName] = OrderedDict()

    def _addWidget(self, tabName, label, widgetClass, widgetParams, configKey):
        """ Add a new widget.

        @param tabName: name of the tab where to add the widget
        @type tabName: str

        @param label: associated label of the option
        @type label: str

        @param widgetClass: widget class to use for the option
        @type widgetClass: QtGui.QWidget

        @param widgetParams: params to give to the widget
        @type widgetParams: tuple

        @param configKey: key for the config.
        @type configKey: str
        """
        self._fields[tabName][label] = {'widget': widgetClass(*widgetParams),
                                        'configKey': configKey}
        self._fields[tabName][label]['widget'].setValue(self._model._config[configKey])

    def _initWidgets(self):
        self._view.setWindowTitle("%s %s" % (self._model.name, self._model.capacity))

        # Create the Gui fields
        self._defineGui()

        # Populate GUI with fields
        widgets = {}
        for tabName in self._fields.keys():
            if tabName == "Main":
                widget = self._view.mainTab
                formLayout =self._view.formLayout
            else:
                widget = QtGui.QWidget(self._view)
                formLayout = QtGui.QFormLayout(widget)
                widget.setLayout(formLayout)
                self._view.tabWidget.addTab(widget, tabName)
                Logger().debug("AbstractPluginController._initWidgets(): created '%s' tab" % tabName)
            for label, field in self._fields[tabName].iteritems():
                widgets[label] = field['widget']
                field['widget'].setParent(widget)
                formLayout.addRow(label, field['widget'])
                Logger().debug("AbstractPluginController._initWidgets(): added '%s' field" % label)

        self._view.adjustSize()

    def _onAccepted(self):
        """ Ok button has been clicked.
        """
        Logger().trace("AbstractPluginController._onAccepted()")
        for tabName in self._fields.keys():
            for label, field in self._fields[tabName].iteritems():
                value = field['widget'].value()
                if isinstance(value, QtCore.QString):
                    value = unicode(value)
                self._model._config[field['configKey']] = value
        Logger().debug("AbstractPluginController._onAccepted(): config=%s" % self._model._config)
        self._model._saveConfig()
        if self._model.isConnected():
            self._model.configure()

    def _defineGui(self):
        """ Define the GUI.

        The widgets for the plugin config. dialog are defined here.
        """
        raise NotImplementedError("AbstractPluginController._defineGui() must be overloaded")

    # Interface
    def refreshView(self):
        pass
