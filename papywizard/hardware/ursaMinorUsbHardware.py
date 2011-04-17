# -*- coding: utf-8 -*-

""" Panohead remote control.

License
=======

 - B{Papywizard} (U{http://www.papywizard.org}) is Copyright:
  - (C) 2007-2011 Frédéric Mantegazza

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

Hardware

Implements
==========

- UrsaMinorUsbHardware

@author: Frédéric Mantegazza
@copyright: (C) 2010-2011 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

from PyQt4 import QtCore, QtGui

from papywizard.common import config
from papywizard.common.loggingServices import Logger
from papywizard.hardware.abstractHardware import AbstractHardware


class UrsaMinorUsbHardware(AbstractHardware):
    """ UrsaMinor Usb interface low-level hardware.
    """
    def _init(self):
        AbstractHardware._init(self)
        self.__triggerLine = None
        self.__triggerLineInverted = None

    def __xor(self, a, b):
        """ XOR logical expression.
        """
        return (a and not b) or (not a and b)

    def setTriggerLine(self, line):
        """ Set the trigger line.
        """
        self.__triggerLine = line

    def setTriggerLineInverted(self, inverted):
        """ Invert or not the trigger line signal.
        """
        self.__triggerLineInverted = inverted

    def setOutput(self, state):
        """ Set the output state.
        """
        self._driver.acquireBus()
        try:
            method = getattr(self._driver, "set%s" % self.__triggerLine)
            method(self.__xor(state, self.__triggerLineInverted))
        finally:
            self._driver.releaseBus()

    def shutdown(self):
        self._driver.acquireBus()
        try:
            self.setOutput(False)
        finally:
            self._driver.releaseBus()
