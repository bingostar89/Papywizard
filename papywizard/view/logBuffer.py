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

View.

@author: Frédéric Mantegazza
@copyright: (C) 2007-2008 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id: config.py 527 2008-09-16 14:10:08Z fma $"

import pygtk
pygtk.require("2.0")
import gtk

from papywizard.common import config


class LogBuffer(gtk.TextBuffer):
    """ Log buffer storage.

    Implement a log buffer, which automatically appends
    a log at the end, with the right color, and limit the
    buffer size to a specified value.

    To be used within a gtk.TextView.
    """
    def __init__(self, *args, **kwargs):
        """ Init the log buffer.
        """
        super(LogBuffer, self).__init__(*args, **kwargs)

        self.create_tag('TRACE', foreground='blue', background='black', font="courrier 8")
        self.create_tag('DEBUG', foreground='lightblue', background='black', font="courrier 8")
        self.create_tag('INFO', foreground='white', background='black', font="courrier 8")
        self.create_tag('WARNING', foreground='yellow', background='black', font="courrier 8")
        self.create_tag('ERROR', foreground='red', background='black', font="courrier 8")
        self.create_tag('EXCEPTION', foreground='purple', background='black', font="courrier 8")
        self.create_tag('CRITICAL', foreground='white', background='black', font="courrier 8")

    def write(self, logMessage):
        """ write a log message a the end of the buffer.

        @param logMessage: log to write
        @type logMessage: str

        @todo: check if we are in the GTK main thread;
               ff not, need to use the serializer
        """
        self.begin_user_action()
        try:
            try:
                level = logMessage.split('::')[2]
                self.insert_with_tags_by_name(self.get_end_iter(), logMessage, level)
            except IndexError:
                self.insert_with_tags_by_name(self.get_end_iter(), logMessage, 'INFO')
            overflow = self.get_line_count() - config.LOGGER_MAX_COUNT_LINE
            if overflow > 0:
                self.delete(self.get_iter_at_line(0), self.get_iter_at_line(overflow))
                # todo: scroll to the bottom of the buffer
        finally:
            self.end_user_action()

    def clear(self):
        """ Clear the log window.
        """
        self.begin_user_action()
        try:
            self.delete(*self.get_bounds())
        finally:
            self.end_user_action()

    def flush():
        """ Dummy method.

        Needed to use this class as logging stream.
        """
        pass
