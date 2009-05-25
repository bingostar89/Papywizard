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

Logging

Implements
==========

- DefaultFormatter
- ColorFormatter
- Logger

@author: Frédéric Mantegazza
@copyright: (C) 2007-2009 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

import logging
import logging.handlers
import StringIO
import traceback
import os.path

from PyQt4 import QtCore

from papywizard.common import config
from papywizard.common.loggingFormatter import DefaultFormatter, ColorFormatter, \
                                               SpaceFormatter, SpaceColorFormatter

logger = None


class LoggerObject(QtCore.QObject):
    """ Logger object.
    """
    def __init__(self, defaultStreamHandler, defaultFileHandler):
        """ Init object.
        """
        logging.TRACE = logging.DEBUG - 5
        logging.EXCEPTION = logging.ERROR + 5
        logging.raiseExceptions = 0
        logging.addLevelName(logging.TRACE, "TRACE")
        logging.addLevelName(logging.EXCEPTION, "EXCEPTION")

        # Formatters
        #defaultFormatter = DefaultFormatter(config.LOGGER_FORMAT)
        spaceFormatter = SpaceFormatter(config.LOGGER_FORMAT)
        #colorFormatter = ColorFormatter(config.LOGGER_FORMAT)
        spaceColorFormatter = SpaceColorFormatter(config.LOGGER_FORMAT)

        # Logger
        self.__logger = logging.getLogger('papywizard')
        self.__logger.setLevel(logging.TRACE)

        # Handlers
        if defaultStreamHandler:
            stdoutStreamHandler = logging.StreamHandler()
            #stdoutStreamHandler.setFormatter(colorFormatter)
            stdoutStreamHandler.setFormatter(spaceColorFormatter)
            self.__logger.addHandler(stdoutStreamHandler)
        if defaultFileHandler:
            loggerFilename = os.path.join(config.TMP_DIR, config.LOGGER_FILENAME)
            fileHandler = logging.handlers.RotatingFileHandler(loggerFilename, 'w',
                                                               config.LOGGER_MAX_BYTES,
                                                               config.LOGGER_BACKUP_COUNT)
            fileHandler.setFormatter(spaceFormatter)
            self.__logger.addHandler(fileHandler)

    def addStreamHandler(self, stream, formatter=DefaultFormatter):
        """ Add a new stream handler.

        Can be used to register a new GUI handler.

        @param stream: open stream where to write logs
        @type stream: ???

        @param formatter: associated formatter
        @type formatter: L{DefaultFormatter<common.loggingFormatter>}
        """
        handler = logging.StreamHandler(stream)
        handler.setFormatter(formatter(config.LOGGER_FORMAT))
        self.__logger.addHandler(handler)

    def setLevel(self, level):
        """ Change logging level.

        @param level: new level, in ('trace', 'debug', 'info', 'warning', 'error', 'exception', 'critical')
        @type level: str
        """
        loggerLevels = ('trace', 'debug', 'info', 'warning', 'error', 'exception', 'critical')
        if level not in loggerLevels:
            raise ValueError("Logger level must be in %s" % loggerLevels)
        levels = {'trace': logging.TRACE,
                  'debug': logging.DEBUG,
                  'info': logging.INFO,
                  'warning': logging.WARNING,
                  'error': logging.ERROR,
                  'exception': logging.EXCEPTION,
                  'critical': logging.CRITICAL}
        self.__logger.setLevel(levels[level])

    def trace(self, message):
        """ Logs a message with level TRACE.

        @param message: message to log
        @type message: string
        """
        self.__logger.log(logging.TRACE, message)

    def debug(self, message):
        """ Logs a message with level DEBUG.

        @param message: message to log
        @type message: string
        """
        self.__logger.debug(message)

    def info(self, message):
        """ Logs a message with level INFO.

        @param message: message to log
        @type message: string
        """
        self.__logger.info(message)

    def warning(self, message):
        """ Logs a message with level WARNING.

        @param message: message to log
        @type message: string
        """
        self.__logger.warning(message)

    def error(self, message):
        """ Logs a message with level ERROR.

        @param message: message to log
        @type message: string
        """
        self.__logger.error(message)

    def critical(self, message):
        """ Logs a message with level CRITICAL.

        @param message: message to log
        @type message: string
        """
        self.__logger.critical(message)

    def exception(self, message="", debug=False):
        """ Logs a message within an exception.

        @param message: message to log
        @type message: string

        @param debug: flag to log exception on DEBUG level instead of EXCEPTION one
        @type debug: bool
        """
        #self.__logger.exception(message)

        tracebackString = StringIO.StringIO()
        traceback.print_exc(file=tracebackString)
        message += "\n"+tracebackString.getvalue().strip()
        tracebackString.close()
        if debug:
            self.debug(message)
        else:
            self.log(logging.EXCEPTION, message)

    def log(self, level, message, *args, **kwargs):
        """ Logs a message with given level.

        @param level: log level to use
        @type level: int

        @param message: message to log
        @type message: string
        """
        self.__logger.log(level, message, *args, **kwargs)

    def getTraceback(self):
        """ Return the complete traceback.

        Should be called in an except statement.
        """
        tracebackString = StringIO.StringIO()
        traceback.print_exc(file=tracebackString)
        message = tracebackString.getvalue().strip()
        tracebackString.close()
        return message

    def shutdown(self):
        """ Shutdown the logging service.
        """
        logging.shutdown()


# Logger factory
def Logger(defaultStreamHandler=True, defaultFileHandler=True):
    global logger
    if logger is None:
        logger = LoggerObject(defaultStreamHandler, defaultFileHandler)

    return logger
