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

- PluginsStatusController

@author: Frédéric Mantegazza
@copyright: (C) 2007-2009 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

from PyQt4 import QtCore, QtGui

from papywizard.common.loggingServices import Logger
from papywizard.controller.abstractController import AbstractModalDialogController


class PluginsStatusController(AbstractModalDialogController):
    """ Plugins status controller object.
    """
    def _init(self):
        self._uiFile = "pluginsStatusDialog.ui"

    def _initWidgets(self):
        pass

    # Helpers
    def __setStatus(self, widget, status):
        """ Fill the widget according tostatus.

        @param widget: widget to use
        @type widget: QtGui.QWidget

        @param status: status of the plugin
        @type status: bool
        """
        if status:
            widget.setPixmap(QtGui.QPixmap(":/icons/button_ok.png").scaled(16, 16))
        else:
            widget.setPixmap(QtGui.QPixmap(":/icons/button_cancel.png").scaled(16, 16))

    # Callbacks

    # Interface
    def refreshView(self):
        self.__setStatus(self._view.yawStartStopLabel, self._model['yawAxis']['connect'])
        self.__setStatus(self._view.yawInitShutdownLabel, self._model['yawAxis']['init'])
        self.__setStatus(self._view.pitchStartStopLabel, self._model['pitchAxis']['connect'])
        self.__setStatus(self._view.pitchInitShutdownLabel, self._model['pitchAxis']['init'])
        self.__setStatus(self._view.shutterStartStopLabel, self._model['shutter']['connect'])
        self.__setStatus(self._view.shutterInitShutdownLabel, self._model['shutter']['init'])
