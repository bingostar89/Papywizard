# -*- coding: iso-8859-1 -*-

""" Panohead remote control.

Model.

Implements class:

- Camera

@author: Frederic Mantegazza
@copyright: 2007
@license: CeCILL
@todo:
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

        # Load Camera attributes from preferences
        self.sensorRatio = ConfigManager().get('Preferences', 'CAMERA_SENSOR_RATIO')
        self.sensorCoef = ConfigManager().getFloat('Preferences', 'CAMERA_SENSOR_COEF')
        self.timeValue = ConfigManager().getFloat('Preferences', 'CAMERA_TIME_VALUE')
        self.nbPicts = ConfigManager().getInt('Preferences', 'CAMERA_NB_PICTS')

    def getYawFov(self, cameraOrientation):
        """ Compute the yaw FoV.

        @return: yaw FoV of the image
        @rtype: float

        @todo: handle 4:3 format
        """
        if cameraOrientation == 'landscape':
            sensorSize = 36.
        elif cameraOrientation == 'portrait':
            sensorSize = 24.

        return self.lens.computeFov(sensorSize / self.sensorCoef)

    def getPitchFov(self, cameraOrientation):
        """ Compute the pitch FoV.

        @return: pitch FoV of the image
        @rtype: float

        @todo: handle 4:3 format
        """
        if cameraOrientation == 'landscape':
            sensorSize = 24.
        elif cameraOrientation == 'portrait':
            sensorSize = 36.

        return self.lens.computeFov(sensorSize / self.sensorCoef)

    def shutdown(self):
        """ Cleanly terminate the camera.

        Save values to preferences.
        """
        Logger().trace("Camera.shutdown()")
        self.lens.shutdown()

        ConfigManager().set('Preferences', 'CAMERA_SENSOR_RATIO', self.sensorRatio)
        ConfigManager().setFloat('Preferences', 'CAMERA_SENSOR_COEF', self.sensorCoef, 1)
        ConfigManager().setFloat('Preferences', 'CAMERA_TIME_VALUE', self.timeValue, 1)
        ConfigManager().setInt('Preferences', 'CAMERA_NB_PICTS', self.nbPicts)
