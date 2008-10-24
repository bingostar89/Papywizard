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

- LoggerController

@author: Frédéric Mantegazza
@copyright: (C) 2007-2008 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id: configController.py 523 2008-09-16 14:03:24Z fma $"

import os.path

import pygtk
pygtk.require("2.0")
import gtk
import gtk.gdk

from papywizard.common import config
from papywizard.common.loggingServices import Logger
from papywizard.common.configManager import ConfigManager
from papywizard.controller.abstractController import AbstractController


class LoggerController(AbstractController):
    """ Logger controller object.
    """
    def _init(self):
        self._gladeFile = "loggerDialog.glade"
        self._signalDict = {"on_clearButton_clicked": self.__onClearButtonClicked,
                            "on_saveButton_clicked": self.__onSaveButtonClicked,
                            "on_doneButton_clicked": self.__onDoneButtonClicked,
                        }

    def _retreiveWidgets(self):
        """ Get widgets from widget tree.
        """
        super(LoggerController, self)._retreiveWidgets()

        self.loggerScrolledwindow = self.wTree.get_widget("loggerScrolledwindow")
        self.loggerTextview = self.wTree.get_widget("loggerTextview")
        self.loggerTextview.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse('black'))

        # The following code is taken from pychess project;
        # it keeps the scroller at the bottom of the text
        # Thanks to Thomas Dybdahl Ahle who sent it to me
        def changed(vadjust):
            if not hasattr(vadjust, "need_scroll") or vadjust.need_scroll:
                vadjust.set_value(vadjust.upper-vadjust.page_size)
                vadjust.need_scroll = True
        self.loggerScrolledwindow.get_vadjustment().connect("changed", changed)

        def value_changed(vadjust):
            vadjust.need_scroll = abs(vadjust.value + vadjust.page_size - vadjust.upper) < vadjust.step_increment
        self.loggerScrolledwindow.get_vadjustment().connect("value-changed", value_changed)

    # Callbacks
    def __onClearButtonClicked(self, widget):
        """ Clear button has been clicked.
        """
        Logger().trace("LoggerController.__onClearButtonClicked()")
        self.loggerTextview.get_buffer().clear()

    def __onSaveButtonClicked(self, widget):
        """ Save button has been clicked.
        """
        Logger().trace("LoggerController.__onSaveButtonClicked()")
        fileDialog = gtk.FileChooserDialog(title="Save log", parent=self.dialog,
                                           action=gtk.FILE_CHOOSER_ACTION_SAVE,
                                           buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                                                    gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
        filter = gtk.FileFilter()
        filter.set_name("log files")
        filter.add_pattern("*.log")
        fileDialog.add_filter(filter)
        filter = gtk.FileFilter()
        filter.set_name("all files")
        filter.add_pattern("*.*")
        fileDialog.add_filter(filter)
        dataStorageDir = ConfigManager().get('Data', 'DATA_STORAGE_DIR')
        fileDialog.set_filename(os.path.join(dataStorageDir, config.LOGGER_FILENAME))
        fileDialog.set_current_name(unicode(config.LOGGER_FILENAME).encode('utf-8'))
        response = fileDialog.run()
        if response == gtk.RESPONSE_ACCEPT:
            logFileName = fileDialog.get_filename()
            buffer_ = self.loggerTextview.get_buffer()
            logText = buffer_.get_text(buffer.get_start_iter(), buffer.get_end_iter())
            logFile = file(logFileName, 'w')
            logFile.write(logText)
            logFile.close()
        fileDialog.destroy()

    def __onDoneButtonClicked(self, widget):
        """ Done button has been clicked.
        """
        Logger().trace("LoggerController.__onDoneButtonClicked()")
        self.dialog.response(0)

    # Real work
    def refreshView(self):
        pass

    def setLogBuffer(self, buffer):
        """ Set the associated buffer.

        @param buffer: associated buffer
        @type buffer: gtk.TextBuffer
        """
        self.loggerTextview.set_buffer(buffer)
