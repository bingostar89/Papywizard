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

Message dialog controller

Implements
==========

- BaseMessageController
- InfoMessageController
- WarningMessageController
- ErrorDialogController
- ExceptionMessageController


@author: Frédéric Mantegazza
@copyright: (C) 2007-2008 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

import traceback
import StringIO

import pygtk
pygtk.require("2.0")
import gtk

_ = lambda a: a


class BaseMessageController(object):
    """ Abstract message controller.
    """
    def __init__(self, subTitle, message):
        """ Init the base message controller.

        @param subTitle: dialog subTitle
        @type subTitle: str

        @param message: dialog message
        @type message: str
        """
        self.__dialog = self._createMessageDialog(subTitle)
        self.__dialog.format_secondary_text(message)

    def run(self):
        """ Run the dialog.
        
        @return: response
        @rtype: int
        """
        response = self.__dialog.run()
        self.__dialog.destroy()
        return response

    def _createMessageDialog(self, subTitle, message):
        dialog = gtk.MessageDialog(flags=gtk.DIALOG_MODAL, type=type_, buttons=gtk.BUTTONS_CLOSE,
                                   message_format=subTitle)
        dialog.set_title(title)
        dialog.format_secondary_text(message)
        return dialog


class InfoMessageController(BaseMessageController):
    """ Info message controller.
    """
    def _createMessageDialog(self, subTitle):
        dialog = gtk.MessageDialog(flags=gtk.DIALOG_MODAL, type=gtk.MESSAGE_INFO, buttons=gtk.BUTTONS_CLOSE,
                                   message_format=subTitle)
        dialog.set_title("Info")
        return dialog


class WarningMessageController(BaseMessageController):
    """ Warning message controller.
    """
    def _createMessageDialog(self, subTitle):
        dialog = gtk.MessageDialog(flags=gtk.DIALOG_MODAL, type=gtk.MESSAGE_WARNING, buttons=gtk.BUTTONS_CLOSE,
                                   message_format=subTitle)
        dialog.set_title("Warning")
        return dialog


class ErrorMessageController(BaseMessageController):
    """ Error message controller.
    """
    def _createMessageDialog(self, subTitle):
        dialog = gtk.MessageDialog(flags=gtk.DIALOG_MODAL, type=gtk.MESSAGE_ERROR, buttons=gtk.BUTTONS_CLOSE,
                                   message_format=subTitle)
        dialog.set_title("Error")
        return dialog


class YesNoMessageController(BaseMessageController):
    """ Yes/No question message controller.
    """
    def _createMessageDialog(self, subTitle):
        dialog = gtk.MessageDialog(flags=gtk.DIALOG_MODAL, type=gtk.MESSAGE_QUESTION,
                                   buttons=gtk.BUTTONS_YES_NO,
                                   message_format=subTitle)
        dialog.set_title("Question")
        dialog.set_default_response(gtk.RESPONSE_YES)
        return dialog


class ExceptionMessageController(object):
    """ Exception message controller.
    """
    def __init__(self, from_):
        """ Init the exception message controller.

        @param from_: function/method name where the exception occured
        @type from_: str
        """
        tracebackString = StringIO.StringIO()
        traceback.print_exc(file=tracebackString)
        message = tracebackString.getvalue().strip()
        tracebackString.close()
        self.__dialog = gtk.Dialog(flags=gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                   buttons=(gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE))
        self.__dialog.set_title("Exception")
        label = gtk.Label("An exception occured in '%s'" % from_)
        self.__dialog.vbox.pack_start(label, expand=False)
        scolledWindow = gtk.ScrolledWindow()
        textView = gtk.TextView()
        textBuffer = gtk.TextBuffer()
        textBuffer.set_text(message)
        textView.set_buffer(textBuffer)
        scolledWindow.add_with_viewport(textView)
        self.__dialog.vbox.pack_start(scolledWindow)
        self.__dialog.vbox.set_spacing(5)
        self.__dialog.set_size_request(500, 300)
        self.__dialog.vbox.show_all()

    def run(self):
        """ Run the dialog.
        
        @return: response
        @rtype: int
        """
        response = self.__dialog.run()
        self.__dialog.destroy()
        return response
