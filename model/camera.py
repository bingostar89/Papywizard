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

from papywizard.common.loggingServices import Logger
from papywizard.common.preferences import Preferences
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
        self.__prefs = Preferences().load()
        self.sensorRatio = self.__prefs['camera']['sensorRatio']
        self.sensorCoef = self.__prefs['camera']['sensorCoef']
        self.timeValue = self.__prefs['camera']['timeValue']
        self.nbPicts = self.__prefs['camera']['nbPicts']

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

        self.__prefs['camera']['sensorRatio'] = self.sensorRatio
        self.__prefs['camera']['sensorCoef'] = self.sensorCoef
        self.__prefs['camera']['timeValue'] = self.timeValue
        self.__prefs['camera']['nbPicts'] = self.nbPicts
