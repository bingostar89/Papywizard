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


class DefaultFormatter(logging.Formatter):
    """ Formateur par défaut pour les subscribers.
    """


class ColorFormatter(DefaultFormatter):
    """ Formatage avec couleurs.
    """
    if sys.platform == 'linux2':
        colors = {'trace':"\033[0;36;40;22m",     # cyan/noir, normal
                  'debug':"\033[0;36;40;1m",      # cyan/noir, gras
                  'info':"\033[0;37;40;1m",       # blanc/noir, gras
                  'warning':"\033[0;33;40;1m",    # marron/noir, gras
                  'error':"\033[0;31;40;1m",      # rouge/noir, gras
                  'exception':"\033[0;35;40;1m",  # magenta/noir, gras
                  'critical':"\033[0;37;41;1m",   # blanc/rouge, gras
                  'default':"\033[0m",            # defaut
                  }
    else:
        colors = {'trace':"",
                  'debug':"",
                  'info':"",
                  'warning':"",
                  'error':"",
                  'exception':"",
                  'critical':"",
                  'default':"",
                  }

    def _toColor(self, msg, levelname):
        """ Colorize.
        """
        if levelname == 'TRACE':
            color = ColorFormatter.colors['trace']
        elif levelname == 'DEBUG':
            color = ColorFormatter.colors['debug']
        elif  levelname in 'INFO':
            color = ColorFormatter.colors['info']
        elif levelname == 'COMMENT':
            color = ColorFormatter.colors['comment']
        elif levelname == 'PROMPT':
            color = ColorFormatter.colors['prompt']
        elif levelname == 'WARNING':
            color = ColorFormatter.colors['warning']
        elif levelname == 'ERROR':
            color = ColorFormatter.colors['error']
        elif levelname == 'EXCEPTION':
            color = ColorFormatter.colors['exception']
        elif levelname == 'CRITICAL':
            color = ColorFormatter.colors['critical']
        else:
            color = ColorFormatter.colors['default']

        return color + msg + ColorFormatter.colors['default']

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


class SpaceColorFormatter(SpaceFormatter, ColorFormatter):
    """ Formatter avec couleurs et sauts de lignes.
    """
    def format(self, record):
        msg = SpaceFormatter.format(self, record)
        return self._toColor(msg, record.levelname)
