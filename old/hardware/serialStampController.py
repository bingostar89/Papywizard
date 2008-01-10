# -*- coding: iso-8859-1 -*-

""" Panohead remote control.

Hardware classes.

Implements class:

- SerialStampController

@author: Frederic Mantegazza
@copyright: 2007
@license: CeCILL
@todo:
"""

__revision__ = "$Id$"

import time

from common.loggingServices import Logger
from serialController import SerialController


class SerialStampController(SerialController):
    """ Stamp controller.
    
    This controller uses a Basic Stamp to drive the head.
    """
    def sendCmd(self, cmd):
        self.acquireBus()
        try:
            self.write(":%s\r" % cmd)
            c = ''
            while c != '=':
                c = self.read(1)
                if not c:
                    raise IOError("Timeout while reading on serial bus")
            data = ""
            while True:
                c = self.read(1)
                if not c:
                    raise IOError("Timeout while reading on serial bus")
                elif c == '\r':
                    break
                data += c
                
            # Wait a few ms to let the BS2 accept new commands
            time.sleep(0.05)
            
        finally:
            self.releaseBus()
            
        return data
