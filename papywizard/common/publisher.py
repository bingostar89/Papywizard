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

This module implements a head position publisher mecanism. It listens
on a socket, waiting for incoming clients connection. Each time the head
position changes, it publishes the new position to all connected
clients.

Implements
==========

- PublisherHandler
- PublisherServer
- Publisher

@author: Frédéric Mantegazza
@copyright: (C) 2007-2009 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

import time
import threading
import socket
import SocketServer

from papywizard.common import config
from papywizard.common.loggingServices import Logger
from papywizard.controller.spy import Spy


class PublisherHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        Logger().debug("PublisherHandler.handle(): new connection from %s:%d" % self.client_address)
        Spy().newPosSignal.connect(self.__newPosition)
        Spy().execute(force=True)

        # Wait forever
        while Spy().isRunning():
            time.sleep(.1)

    def __newPosition(self, yaw, pitch):
        """ Signal callback.
        """
        #Logger().debug("PublisherHandler.__newPosition(): yaw=%.1f, pitch=%.1f" % (yaw, pitch))
        try:
            #Logger().debug("PublisherHandler.__newPosition(): sending to %s:%d" % self.client_address)
            self.request.sendall("%f, %f" % (yaw, pitch))
        except socket.error, msg:
            Logger().exception("PublisherHandler.__newPosition()")
            self.request.close()
            Spy().newPosSignal.disconnect(self.__newPosition)
            Logger().debug("PublisherHandler.handle(): connection from %s:%d closed" % self.client_address)


class PublisherServer(SocketServer.ThreadingTCPServer):
    allow_reuse_address = True

    def handle_error(self, request, client_address):
        Logger().exception("PublisherServer.handle_error()")
        Logger().error("Error while handling request from ('%s', %d)" % client_address)


class Publisher(threading.Thread):
    """ Publisher object.
    """
    def __init__(self):
        """ Init the publisher.
        """
        threading.Thread.__init__(self)
        self.setDaemon(1)
        self.setName("Publisher")
        try:
            self.__server = PublisherServer((config.PUBLISHER_HOST, config.PUBLISHER_PORT), PublisherHandler)
        except socket.error, error:
            Logger().exception("Publisher.__init__()")
            err, msg = tuple(error)
            raise socket.error(msg)

    def run(self):
        """ Main entry of the thread.
        """
        Logger().info("Starting Publisher...")
        self.__server.serve_forever()
        Logger().info("Publisher stopped")
