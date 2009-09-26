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

Graphical toolkit extensions

Implements
==========

- DefaultFormatter
- ColorFormatter
- SpaceFormatter
- SpaceColorFormatter

@author: Frédéric Mantegazza
@copyright: (C) 2007-2009 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

import logging
import time
import sys
if sys.platform == 'win32':
    from ctypes import windll
    STD_INPUT_HANDLE = -10
    STD_OUTPUT_HANDLE = -11
    STD_ERROR_HANDLE = -12
    stderrHandle = windll.kernel32.GetStdHandle(STD_ERROR_HANDLE)
    stdoutHandle = windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
    setConsoleTextAttribute = windll.kernel32.SetConsoleTextAttribute


class DefaultFormatter(logging.Formatter):
    """ Formateur par défaut pour les subscribers.
    """


class LinuxColorFormatter(DefaultFormatter):
    """ Colors for linux console.
    """
    colors = {'trace': "\033[0;36;40;22m",     # cyan/noir, normal
              'debug': "\033[0;36;40;1m",      # cyan/noir, gras
              'info': "\033[0;37;40;1m",       # blanc/noir, gras
              'warning': "\033[0;33;40;1m",    # jaune/noir, gras
              'error': "\033[0;31;40;1m",      # rouge/noir, gras
              'exception': "\033[0;35;40;1m",  # magenta/noir, gras
              'critical': "\033[0;37;41;1m",   # blanc/rouge, gras
              'default': "\033[0m",            # defaut
              }

    def _toColor(self, msg, levelname):
        """ Colorize.
        """
        if levelname == 'TRACE':
            color = LinuxColorFormatter.colors['trace']
        elif levelname == 'DEBUG':
            color = LinuxColorFormatter.colors['debug']
        elif  levelname in 'INFO':
            color = LinuxColorFormatter.colors['info']
        elif levelname == 'COMMENT':
            color = LinuxColorFormatter.colors['comment']
        elif levelname == 'PROMPT':
            color = LinuxColorFormatter.colors['prompt']
        elif levelname == 'WARNING':
            color = LinuxColorFormatter.colors['warning']
        elif levelname == 'ERROR':
            color = LinuxColorFormatter.colors['error']
        elif levelname == 'EXCEPTION':
            color = LinuxColorFormatter.colors['exception']
        elif levelname == 'CRITICAL':
            color = LinuxColorFormatter.colors['critical']
        else:
            color = LinuxColorFormatter.colors['default']

        return color + msg + LinuxColorFormatter.colors['default']

    def format(self, record):
        msg = DefaultFormatter.format(self, record)
        return self._toColor(msg, record.levelname)


class WindowsColorFormatter(DefaultFormatter):
    """ Colors for Windows console.
    """
    FOREGROUND_BLACK     = 0x0000
    FOREGROUND_BLUE      = 0x0001
    FOREGROUND_GREEN     = 0x0002
    FOREGROUND_CYAN      = 0x0003
    FOREGROUND_RED       = 0x0004
    FOREGROUND_MAGENTA   = 0x0005
    FOREGROUND_YELLOW    = 0x0006
    FOREGROUND_GREY      = 0x0007
    FOREGROUND_INTENSITY = 0x0008 # foreground color is intensified.

    BACKGROUND_BLACK     = 0x0000
    BACKGROUND_BLUE      = 0x0010
    BACKGROUND_GREEN     = 0x0020
    BACKGROUND_CYAN      = 0x0030
    BACKGROUND_RED       = 0x0040
    BACKGROUND_MAGENTA   = 0x0050
    BACKGROUND_YELLOW    = 0x0060
    BACKGROUND_GREY      = 0x0070
    BACKGROUND_INTENSITY = 0x0080 # background color is intensified.

    colors = {'trace': FOREGROUND_CYAN | BACKGROUND_BLACK,                                # cyan/noir, normal
              'debug': FOREGROUND_CYAN | BACKGROUND_BLACK | FOREGROUND_INTENSITY,         # cyan/noir, gras
              'info': FOREGROUND_GREY | BACKGROUND_BLACK | FOREGROUND_INTENSITY,          # blanc/noir, gras
              'warning': FOREGROUND_YELLOW | BACKGROUND_BLACK | FOREGROUND_INTENSITY,     # jaune/noir, gras
              'error': FOREGROUND_RED | BACKGROUND_BLACK | FOREGROUND_INTENSITY,          # rouge/noir, gras
              'exception': FOREGROUND_MAGENTA | BACKGROUND_BLACK | FOREGROUND_INTENSITY,  # magenta/noir, gras
              'critical': FOREGROUND_GREY | BACKGROUND_RED | FOREGROUND_INTENSITY,        # blanc/rouge, gras
              'default': FOREGROUND_GREY | BACKGROUND_BLACK,                              # defaut
              }

    def _setTextAttribute(self, color):
        """ Sets the character attributes (colors).
        
        Color is a combination of foreground and background color,
        foreground and background intensity.
        """
        setConsoleTextAttribute(stderrHandle, color)

    def _toColor(self, msg, levelname):
        """ Colorize.
        """
        if levelname == 'TRACE':
            self._setTextAttribute(WindowsColorFormatter.colors['trace'])
        elif levelname == 'DEBUG':
            self._setTextAttribute(WindowsColorFormatter.colors['debug'])
        elif  levelname == 'INFO':
            self._setTextAttribute(WindowsColorFormatter.colors['info'])
        elif levelname == 'COMMENT':
            self._setTextAttribute(WindowsColorFormatter.colors['comment'])
        elif levelname == 'PROMPT':
            self._setTextAttribute(WindowsColorFormatter.colors['prompt'])
        elif levelname == 'WARNING':
            self._setTextAttribute(WindowsColorFormatter.colors['warning'])
        elif levelname == 'ERROR':
            self._setTextAttribute(WindowsColorFormatter.colors['error'])
        elif levelname == 'EXCEPTION':
            self._setTextAttribute(WindowsColorFormatter.colors['exception'])
        elif levelname == 'CRITICAL':
            self._setTextAttribute(WindowsColorFormatter.colors['critical'])
        else:
            self._setTextAttribute(WindowsColorFormatter.colors['default'])

        return msg

    def format(self, record):
        msg = DefaultFormatter.format(self, record)
        return self._toColor(msg, record.levelname)


class SpaceFormatter(DefaultFormatter):
    """ Formatage avec sauts de lignes.
    """
    _lastLogTime = time.time()

    def _addSpace(self, msg):
        """ Ajoute des lignes vides.

        Le nombre de lignes vide est fonction du temps écoulé depuis
        le dernier enregistrement émis.
        """
        if time.time() - SpaceFormatter._lastLogTime > 3600:
            space = "\n\n\n"
        elif time.time() - self._lastLogTime > 60:
            space = "\n\n"
        elif time.time() - self._lastLogTime > 3:
            space = "\n"
        else:
           space = ""
        SpaceFormatter._lastLogTime = time.time()

        return space + msg

    def format(self, record):
        msg = DefaultFormatter.format(self, record)
        return self._addSpace(msg)


class LinuxSpaceColorFormatter(SpaceFormatter, LinuxColorFormatter):
    """ Formatter linux avec couleurs et sauts de lignes.
    """
    def format(self, record):
        msg = SpaceFormatter.format(self, record)
        return self._toColor(msg, record.levelname)


class WindowsSpaceColorFormatter(SpaceFormatter, WindowsColorFormatter):
    """ Formatter windows avec couleurs et sauts de lignes.
    """
    def format(self, record):
        msg = SpaceFormatter.format(self, record)
        return self._toColor(msg, record.levelname)


if sys.platform in ('linux2', 'darwin'):
    ColorFormatter = LinuxColorFormatter
    SpaceColorFormatter = LinuxSpaceColorFormatter
elif sys.platform == 'win32':
    ColorFormatter = WindowsColorFormatter
    SpaceColorFormatter = WindowsSpaceColorFormatter
else:
    raise ValueError("Unsupported platform '%s'" % sys.platform)
