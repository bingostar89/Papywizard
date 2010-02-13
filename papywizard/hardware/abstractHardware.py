# -*- coding: utf-8 -*-

""" Panohead remote control.

License
=======

 - B{Papywizard} (U{http://www.papywizard.org}) is Copyright:
  - (C) 2007-2010 Frédéric Mantegazza

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

 - AbstractHardware

@author: Frédéric Mantegazza
@copyright: (C) 2007-2010 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

from PyQt4 import QtCore


class AbstractHardware(QtCore.QObject):
    """ Abstract class for hardware objets.
    """
    def __init__(self):
        """ Init the MerlinOrionHardware object.
        """
        QtCore.QObject.__init__(self)

        self._axis = None
        self._driver = None
        self._nbRetry = 3
        
        self._init()

    def _init(self):
        """" Additionnal init.
        """
        pass

    def setAxis(self, axis):
        """ Set the axis number
        """
        self._axis = axis

    def setDriver(self, driver):
        """ Set the driver to use.
        """
        self._driver = driver

    def setNbRetry(self, nbRetry):
        """ Set the number of retry during com.
        """
        self._nbRetry = nbRetry
