# -*- coding: utf-8 -*-

""" Panohead remote control.

License
=======

 - B{Papywizard} (U{http://www.papywizard.org}) is Copyright:
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

- QDefaultFormatter
- QColorFormatter
- QSpaceFormatter
- QSpaceColorFormatter

@author: Frédéric Mantegazza
@copyright: (C) 2007-2009 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

import logging
import time

from PyQt4 import QtCore

from papywizard.common import config
from papywizard.common.loggingFormatter import DefaultFormatter


class QDefaultFormatter(DefaultFormatter):
    """ Formatage par défaut pour Qt.
    """
    def _toHtml(self, msg):
        """ Convert for html.
        """
        msg = msg.replace('<', "&lt;")
        msg = msg.replace('>', "&gt;")
        msg = msg.replace(' ', "&nbsp;")
        msg = msg.replace('\n', "<br />")
        return msg

    def format(self, record):
        msg = DefaultFormatter.format(self, record)
        return self._toHtml(msg)


class QColorFormatter(QDefaultFormatter):
    """ Formatage avec couleurs.
    """
    colors = {'trace':"<font color=blue>",
              'debug':"<font color=lightblue>",
              'info':"<font color=white>",
              'warning':"<font color=yellow>",
              'error':"<font color=red>",
              'exception':"<font color=violet>",
              'critical':"<font color=white bgcolor=red>",
              'default':"<font color=white>"
              }

    def _toColor(self, msg, levelname):
        """ Colorize.
        """
        if levelname == 'TRACE':
            color = QColorFormatter.colors['trace']
        elif levelname == 'DEBUG':
            color = QColorFormatter.colors['debug']
        elif levelname == 'INFO':
            color = QColorFormatter.colors['info']
        elif levelname == 'WARNING':
            color = QColorFormatter.colors['warning']
        elif levelname == 'ERROR':
            color = QColorFormatter.colors['error']
        elif levelname == 'EXCEPTION':
            color = QColorFormatter.colors['exception']
        elif levelname == 'CRITICAL':
            color = QColorFormatter.colors['critical']
        else:
            color = QColorFormatter.colors['default']

        return color + msg + "</font>"

    def format(self, record):
        msg = QDefaultFormatter.format(self, record)
        return self._toColor(msg, record.levelname)


class QSpaceFormatter(QDefaultFormatter):
    """ Formatage avec sauts de lignes.
    """
    _lastLogTime = time.time()

    def _addSpace(self, msg):
        """ Ajoute des lignes vides.

        Le nombre de lignes vide est fonction du temps écoulé depuis
        le dernier enregistrement émis.
        """
        if time.time() - QSpaceFormatter._lastLogTime > 3600:
            space = "<br /><br /><br />"
        elif time.time() - self._lastLogTime > 60:
            space = "<br /><br />"
        elif time.time() - self._lastLogTime > 3:
            space = "<br />"
        else:
           space = ""
        QSpaceFormatter._lastLogTime = time.time()

        return space + msg

    def format(self, record):
        msg = QDefaultFormatter.format(self, record)
        return self._addSpace(msg)


class QSpaceColorFormatter(QSpaceFormatter, QColorFormatter):
    """ Formatter avec couleurs et sauts de lignes.
    """
    def format(self, record):
        msg = QSpaceFormatter.format(self, record)
        return self._toColor(msg, record.levelname)
