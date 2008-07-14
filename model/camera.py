# -*- coding: iso-8859-1 -*-

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

Model

Implements
==========

- Camera

@author: Frédéric Mantegazza
@copyright: (C) 2007-2008 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

from papywizard.common import config
from papywizard.common.loggingServices import Logger
from papywizard.common.configManager import ConfigManager
from papywizard.model.lens import Lens


class Camera(object):
    """ Camera model.
    """
    def __init__(self):
        """ Init the Camera object.

        Load values from preferences.
        """
        self.lens = Lens()

    def __getSensorRatio(self):
        """
        """
        return ConfigManager().get('Preferences', 'CAMERA_SENSOR_RATIO')
    
    def __setSensorRatio(self, sensorRatio):
        """
        """
        ConfigManager().set('Preferences', 'CAMERA_SENSOR_RATIO', sensorRatio)
        
    sensorRatio = property(__getSensorRatio, __setSensorRatio)
    
    def __getSensorCoef(self):
        """
        """
        return ConfigManager().getFloat('Preferences', 'CAMERA_SENSOR_COEF')
    
    def __setSensorCoef(self, sensorCoef):
        """
        """
        ConfigManager().setFloat('Preferences', 'CAMERA_SENSOR_COEF', sensorCoef, 1)
        
    sensorCoef = property(__getSensorCoef, __setSensorCoef)
    
    def __getTimeValue(self):
        """
        """
        return ConfigManager().getFloat('Preferences', 'CAMERA_TIME_VALUE')
    
    def __setTimeValue(self, timeValue):
        """
        """
        ConfigManager().setFloat('Preferences', 'CAMERA_TIME_VALUE', timeValue, 1)
        
    timeValue = property(__getTimeValue, __setTimeValue)
    
    def __getNbPicts(self):
        """
        """
        return ConfigManager().getInt('Preferences', 'CAMERA_NB_PICTS')
    
    def __setNbPicts(self, nbPicts):
        """
        """
        ConfigManager().setInt('Preferences', 'CAMERA_NB_PICTS', nbPicts)

    nbPicts = property(__getNbPicts, __setNbPicts)

    def getYawFov(self, cameraOrientation):
        """ Compute the yaw FoV.

        @return: yaw FoV of the image
        @rtype: float
        """
        if cameraOrientation == 'landscape':
            sensorSize = 36.
        elif cameraOrientation == 'portrait':
            sensorSize = 36. / config.SENSOR_RATIOS[self.sensorRatio]

        return self.lens.computeFov(sensorSize / self.sensorCoef)

    def getPitchFov(self, cameraOrientation):
        """ Compute the pitch FoV.

        @return: pitch FoV of the image
        @rtype: float
        """
        if cameraOrientation == 'landscape':
            sensorSize = 36. / config.SENSOR_RATIOS[self.sensorRatio]
        elif cameraOrientation == 'portrait':
            sensorSize = 36.

        return self.lens.computeFov(sensorSize / self.sensorCoef)

    def shutdown(self):
        """ Cleanly terminate the camera.

        Save values to preferences.
        """
        Logger().trace("Camera.shutdown()")
        self.lens.shutdown()
