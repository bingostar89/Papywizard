#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Panohead remote control.

License
=======

 - B{papywizard} (U{http://trac.gbiloba.org/papywizard}) is Copyright:
  - (C) 2007-2008 Frédéric Mantegazza

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
@copyright: (C) 2007-2008 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

import time
import sys
import socket

from papywizard.common import config
from papywizard.common.loggingServices import Logger
from papywizard.view3D.view3D import View3D


class BlackHole:
    """ Dummy class for stderr redirection.
    """
    softspace = 0

    def write(self, text): 
        pass


class Papywizard3D(object):
    """ Main 3D application class.
    """
    def __init__(self):
        """ Init the application.
        """
        Logger().setLevel(config.VIEW3D_LOGGER_LEVEL)

    def init(self):
        """ Init the application.
        """

        # Create 3D view
        self.__view3D = View3D("Papywizard3D", scale=(1, 1, 1))
        #Spy().newPosSignal.connect(self.__view3D.draw)
        #Spy().newPosSignal.connect(self.__view3D.viewFromCamera)

        # Create socket for Papywizard main app connection
        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.__run = False

    def run(self):
        """ Run the appliction.
        """
        Logger().info("Starting Papywizard 3D...")
        self.__run = True
        self.__view3D.visible = True

        # Connect to Papywizard main app
        self.__sock.connect((config.PUBLISHER_HOST, config.PUBLISHER_PORT))
        while self.__run:
            data = self.__sock.recv(4096)
            if data:
                data = data.split(',')
                yaw = float(data[0])
                pitch = float(data[1])
                Logger().debug("Papywizard3D.run(): yaw=%.1f, pitch=%.1f" % (yaw, pitch))
                self.__view3D.draw(yaw, pitch)

        Logger().info("Papywizard 3D stopped")

    def shutdown(self):
        """ Stop application.
        """
        self.__run = False


def main():
    if hasattr(sys, "frozen"):
        sys.stderr = BlackHole()

    app = Papywizard3D()
    app.init()
    try:
        app.run()
    except KeyboardInterrupt:
        pass
    app.shutdown()


if __name__ == "__main__":
    main()
