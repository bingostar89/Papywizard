#!/usr/bin/env python
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

Main script for 3D view

@author: Frédéric Mantegazza
@copyright: (C) 2007-2009 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

import time
import sys
import socket

from papywizard.common import config
from papywizard.common.exception import HardwareError
from papywizard.common.loggingServices import Logger
from papywizard.view3D.view3D import View3D


class BlackHole:
    """ Dummy class for stderr redirection.
    """
    softspace = 0

    def write(self, text): 
        pass

def connect():
    """ Connect to server socket.
    """
    Logger().debug("Papywizard3D._connect(): try to connect to server...")
    while True:
        try:

            # Create and connect socket for Papywizard main app connection
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((config.PUBLISHER_HOST, config.PUBLISHER_PORT))
        except socket.error:
            Logger().warning("Can't connect to server. Renewing in 5 s...")
            time.sleep(5)
            continue
        else:
            Logger().debug("Papywizard3D._connect(): connection established")
            break

    return sock


def main():

    # Init the logger
    if hasattr(sys, "frozen"):

        # Forbid all console outputs
        sys.stderr = BlackHole()
        Logger(defaultStream=False)
    else:
        Logger()
    Logger().setLevel(config.VIEW3D_LOGGER_LEVEL)

    # Create 3D view
    view3D = View3D("Papywizard3D", scale=(1, 1, 1))
    view3D.visible = True

    # Enter main loop
    Logger().info("Starting Papywizard 3D...")
    try:
        #sock = connect()
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((config.PUBLISHER_HOST, config.PUBLISHER_PORT))
        while True:
            data = ""
            try:
                data = sock.recv(512)
            except socket.error:
                Logger().exception("Papywizard3D.run()")
            else:
                if data:
                    data = data.split(',')
                    yaw = float(data[0])
                    pitch = float(data[1])
                    Logger().debug("Papywizard3D.run(): yaw=%.1f, pitch=%.1f" % (yaw, pitch))
                    view3D.draw(yaw, pitch)
                else:
                    Logger().warning("Papywizard3D.run(): lost connection with server")
                    time.sleep(1)
                    #sock = connect()

    except KeyboardInterrupt:
        Logger().debug("KeyboardInterrupt")

    Logger().info("Papywizard 3D stopped")


if __name__ == "__main__":
    main()
