# -*- coding: iso-8859-1 -*-

""" Panohead remote control.

License
=======

 - B{papywizard} (U{http://trac.gbiloba.org/papywizard}) is Copyright:
  - (C) 2007-2008 Fr�d�ric Mantegazza

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

@author: Fr�d�ric Mantegazza
@copyright: (C) 2007-2008 Fr�d�ric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id: config.py 527 2008-09-16 14:10:08Z fma $"

import pygtk
pygtk.require("2.0")
import gtk

from papywizard.common import config


class LogBuffer(gtk.TextBuffer):
    """ Log buffer storage.

    To be used with a gtk.TextView.
    """
    def __init__(self, *args, **kwargs):
        """ Init the log buffer.
        """
        super(LogBuffer, self).__init__(*args, **kwargs)

        self.create_tag('TRACE', foreground='darkblue', background='black')
        self.create_tag('DEBUG', foreground='blue', background='black')
        self.create_tag('INFO', foreground='white', background='black')
        self.create_tag('WARNING', foreground='yellow', background='black')
        self.create_tag('ERROR', foreground='red', background='black')
        self.create_tag('EXCEPTION', foreground='purple', background='black')
        self.create_tag('CRITICAL', foreground='white', background='red')

        #tagTable = self.get_tag_table()
        #traceTag = gtk.TextTag(name='TRACE')
        #traceTag.set_property('foreground', 'darkblue')
        #traceTag.set_property('background', 'black')
        #tagTable.add(traceTag)
        #debugTag = gtk.TextTag(name='DEBUG')
        #debugTag.set_property('foreground', 'blue')
        #debugTag.set_property('background', 'black')
        #tagTable.add(debugTag)
        #infoTag = gtk.TextTag(name='INFO')
        #infoTag.set_property('foreground', 'white')
        #infoTag.set_property('background', 'black')
        #tagTable.add(infoTag)
        #warningTag = gtk.TextTag(name='WARNING')
        #warningTag.set_property('foreground', 'yellow')
        #warningTag.set_property('background', 'black')
        #tagTable.add(warningTag)
        #errorTag = gtk.TextTag(name='ERROR')
        #errorTag.set_property('foreground', 'red')
        #errorTag.set_property('background', 'black')
        #tagTable.add(errorTag)
        #exceptionTag = gtk.TextTag(name='EXCEPTION')
        #exceptionTag.set_property('foreground', 'purple')
        #exceptionTag.set_property('background', 'black')
        #tagTable.add(exceptionTag)
        #criticalTag = gtk.TextTag(name='CRITICAL')
        #criticalTag.set_property('foreground', 'white')
        #criticalTag.set_property('background', 'red')
        #tagTable.add(criticalTag)

    def append(self, line):
        """ Append a line to the buffer.

        @param line: line to append
        @type line: str
        """
        self.start_user_action()
        try:
            self.insert_with_tags_by_name(self.get_end_iter(), line, 'DEBUG')
            if self.get_line_count() > config.LOGGER_MAX_COUNT_LINE:
                self.delete(self.get_iter_at_line(0), self.get_iter_at_line(1))
        finally:
            self.end_user_action()

    def clear(self):
        """ Clear teh log window.
        """
        self.start_user_action()
        try:
            self.delete(*self.get_bounds())
        finally:
            self.end_user_action()
