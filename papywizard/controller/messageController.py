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

__revision__ = "$Id: shooting.py 984 2008-10-28 19:37:55Z fma $"

import traceback
import StringIO

import pygtk
pygtk.require("2.0")
import gtk

_ = lambda a: a


class BaseMessageController(object):
    """ Abstract message controller.
    """
    def __init__(self, subTitle, message, type_):
        """ Init the base message controller.

        @param subTitle: dialog subTitle
        @type subTitle: str

        @param message: dialog message
        @type message: str

        @param type_: type of message, in ('error', 'warning', 'info')
        @type type_: str
        """
        if type_ == 'error':
            type_ = gtk.MESSAGE_ERROR
            title = _("Error")
        elif type_ == 'warning':
            type_ = gtk.MESSAGE_WARNING
            title = _("Warning")
        elif type_ == 'info':
            type_ = gtk.MESSAGE_INFO
            title = _("Info")
        else:
            raise ValueError("Message type must be in ('error', 'warning', 'info')")
        messageDialog = gtk.MessageDialog(flags=gtk.DIALOG_MODAL, type=type_, buttons=gtk.BUTTONS_CLOSE,
                                          message_format=subTitle)
        messageDialog.set_title(title)
        messageDialog.format_secondary_text(message)
        messageDialog.run()
        messageDialog.destroy()

class InfoMessageController(BaseMessageController):
    """ Info message controller.
    """
    def __init__(self, subTitle, message):
        super(InfoMessageController, self).__init__(subTitle, message, type_='info')

class WarningMessageController(BaseMessageController):
    """ Warning message controller.
    """
    def __init__(self, subTitle, message):
        super(WarningMessageController, self).__init__(subTitle, message, type_='warning')

class ErrorMessageController(BaseMessageController):
    """ Error message controller.
    """
    def __init__(self, subTitle, message):
        super(ErrorMessageController, self).__init__(subTitle, message, type_='error')

class ExceptionMessageController(BaseMessageController):
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
        super(ExceptionMessageController, self).__init__(from_, message, type_='error')
