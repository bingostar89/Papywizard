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

Hardware driver

Implements
==========

- BusDriver

@author: Frédéric Mantegazza
@copyright: (C) 2007-2009 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

import sets

from PyQt4 import QtCore

from papywizard.common.loggingServices import Logger


class BusDriver(QtCore.QObject):
    """ Base (abstract) class for bus drivers.
    """
    def __init__(self):
        """ Init the object.
        """
        QtCore.QObject.__init__(self)
        self._mutex = QtCore.QMutex(QtCore.QMutex.Recursive)
        self._connected = sets.Set()

    def _init(self):
        """ Init the connection.
        """
        raise NotImplementedError("BusDriver._init() must be overidden")

    def _shutdown(self):
        """ Shutdown the connection.
        """
        raise NotImplementedError("BusDriver._shutdown() must be overidden")

    def establishConnection(self, obj):
        """ An object asks a connection to be established.

        The connection is established only once.
        """
        if not len(self._connected):
            self._init()
        self._connected.add(obj)

    def shutdownConnection(self, obj):
        """ An object asks a connection to be established.

        The connection is shutdown once there are no more
        objects connected.
        """
        if obj in self._connected:
            self._connected.remove(obj)
        if not self._connected:
            self._shutdown()

    def acquireBus(self):
        """ Acquire and lock the bus.
        """
        #Logger().trace("BusDriver.acquireBus()")
        self._mutex.lock()

    def releaseBus(self):
        """ Unlock and release the bus.
        """
        #Logger().trace("BusDriver.releaseBus()")
        self._mutex.unlock()

    def empty(self):
        """ Empty buffer.
        """
        raise NotImplementedError("BusDriver.empty() must be overloaded")

    def write(self, data):
        """ Write data.
        
        @param data: data to write
        @type data: str
        
        @return: size of data written
        @rtype: int
        """
        raise NotImplementedError("BusDriver.write() must be overloaded")

    def read(self, size):
        """ Read data.
        
        @param size: size of the data to read
        @type size: int
        
        @return: read data
        @rtype: str
        """
        raise NotImplementedError("BusDriver.read() must be overloaded")
