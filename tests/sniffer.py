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

Tests

Implements
==========

- Sniffer

@author: Frédéric Mantegazza
@copyright: (C) 2007-2009 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

import serial

from papywizard.common.loggingServices import Logger


SERIAL_PORT = "/dev/ttyS0"
#SERIAL_PORT = "COM1"


class Sniffer(object):
    """ Sniffer object.
    """
    def __init__(self):
        """ Init the Sniffer object.
        """
        self.__serial = serial.Serial(SERIAL_PORT)
        
    def run(self):
        """ Run the sniffer.
        
        Listen to the serial line and display commands/responses.
        """
        Logger().info("Sniffer started")
        try:
            while True:
                data = self.__serial.read()
                if not data:
                    raise IOError("Timeout while reading on serial bus")
                while data[-1] != '\r':
                    c = self.__serial.read()
                    if not c:
                        raise IOError("Timeout while reading on serial bus")
                    else:
                        data += c
                if data[0] == ':':
                    cmd = data[1:-1]
                elif data[0] == '=':
                    resp = data[1:-1]
                    Logger().info("%10s -> %10s" % (cmd, resp))
                else:
                    Logger().debug("%s" % data[1:-1])
        except:
            Logger().exception("Sniffer.run()")
            Logger().info("Sniffer stopped")


def main():
    sniffer = Sniffer()
    sniffer.run()
    
    
if __name__ == "__main__":
    main()
    
