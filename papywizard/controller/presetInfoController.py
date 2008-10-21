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

Graphical toolkit controller

Implements
==========

- PresetTemplateInfoController

@author: Frédéric Mantegazza
@copyright: (C) 2007-2008 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id: configController.py 523 2008-09-16 14:03:24Z fma $"

import pygtk
pygtk.require("2.0")
import gtk
import pango

from papywizard.common.presetManager import PresetManager
from papywizard.common.loggingServices import Logger
from papywizard.controller.abstractController import AbstractController


class PresetTemplateInfoController(AbstractController):
    """ Logger controller object.
    """
    def _init(self):
        self._gladeFile = "presetTemplateInfoDialog.glade"
        self._signalDict = {"on_doneButton_clicked": self.__onDoneButtonClicked,
                        }

    def _retreiveWidgets(self):
        """ Get widgets from widget tree.
        """
        super(PresetTemplateInfoController, self)._retreiveWidgets()

        self.presetTemplateInfoScrolledwindow = self.wTree.get_widget("presetTemplateInfoScrolledwindow")
        self.presetTemplateInfoTextview = self.wTree.get_widget("presetTemplateInfoTextview")
        self.presetTemplateInfoBuffer = gtk.TextBuffer()
        self.presetTemplateInfoBuffer.create_tag('name', foreground='red')
        self.presetTemplateInfoBuffer.create_tag('tooltip', foreground='blue', style=pango.STYLE_OBLIQUE)
        self.presetTemplateInfoTextview.set_buffer(self.presetTemplateInfoBuffer)

    # Callbacks
    def __onDoneButtonClicked(self, widget):
        """ Done button has been clicked.
        """
        Logger().trace("PresetTemplateInfoController.__onDoneButtonClicked()")
        self.dialog.response(0)

    # Real work
    def refreshView(self):
        self.presetTemplateInfoBuffer.begin_user_action()
        try:
            self.presetTemplateInfoBuffer.delete(*self.presetTemplateInfoBuffer.get_bounds())
            presets = PresetManager().getPresets()
            i = 0
            while True:
                try:
                    preset = presets.getByIndex(i)
                    name = "%s\n" % preset.getName()
                    tooltip = "%s\n" % preset.getTooltip()
                    self.presetTemplateInfoBuffer.insert_with_tags_by_name(self.presetTemplateInfoBuffer.get_end_iter(), name, 'name')
                    self.presetTemplateInfoBuffer.insert_with_tags_by_name(self.presetTemplateInfoBuffer.get_end_iter(), tooltip, 'tooltip')
                    i += 1
                except KeyError:
                    break
        finally:
            self.presetTemplateInfoBuffer.end_user_action()
