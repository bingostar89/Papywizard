# -*- coding: iso-8859-1 -*-

""" Panohead remote control.

Model.

Implements class:

- Lens

@author: Frederic Mantegazza
@copyright: 2007
@license: CeCILL
@todo:
"""

__revision__ = "$Id$"

import math

from common.loggingServices import Logger
from common.preferences import Preferences


class Lens(object):
    """ Lens model.
    
    Lens orientation is landscape.
    """
    def __init__(self):
        """ Init object.
        
        Load values from preferences.
        """
        self.__prefs = Preferences().load()
        self.focal = self.__prefs['lens']['focal']
        self.fisheye = self.__prefs['lens']['fisheye']
        
        # Load Mosaic db record
    
    def computeFov(self, size):
        """ Compute FoV.
        
        @param size: size of the sensor
        @type size: float
        
        @return: FoV of the lens
        @rtype: float
        """
        if self.fisheye:
            return 360. / math.pi * 2. * math.asin((size / 2.) / (2. * self.focal))
        else:
            return 360. / math.pi * math.atan(size / (2. * self.focal))
    
    def shutdown(self):
        """ Cleanly terminate the lens
        
        Save values to preferences.
        """
        Logger().trace("Lens.shutdown()")
        self.__prefs['lens']['focal'] = self.focal
        self.__prefs['lens']['fisheye'] = self.fisheye
