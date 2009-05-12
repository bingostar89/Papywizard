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

View.

@author: Frédéric Mantegazza
@copyright: (C) 2007-2009 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

import sys

from papywizard.common import config


class LogBuffer(object):
    """ Log buffer storage.

    Implement a log buffer, which automatically appends
    a record at the end, and limit the size to a specified value.
    """
    def __init__(self):
        """ Init the log buffer.
        """
        self.__buffer = []

    def write(self, logMessage):
        """ write a log message a the end of the buffer.

        @param logMessage: log to write
        @type logMessage: str
        """
        self.__buffer.append(logMessage)
        if len(self.__buffer) > config.LOGGER_MAX_COUNT_LINE:
            del self.__buffer[0]

    def flush():
        """ Dummy method.

        Needed to use this class as logging stream.
        """
        pass

    def getHtml(self):
        text = u""
        for line in self.__buffer:
            if isinstance(line, str):
                text += u"<br />" + line.decode(sys.getfilesystemencoding())
            else:
                text += u"<br />" + line
        return text

    def clear(self):
        """ Clear the buffer.
        """
        self.__buffer = []
