# -*- coding: utf-8 -*-

""" Panohead remote control.

License
=======

 - B{Papywizard} (U{http://www.papywizard.org}) is Copyright:
  - (C) 2007-2011 Frédéric Mantegazza

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
@copyright: (C) 2007-2011 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

import math

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

    def __getSensorCoef(self):
        """
        """
        return ConfigManager().getFloat('Configuration/CAMERA_SENSOR_COEF')

    def __setSensorCoef(self, sensorCoef):
        """
        """
        ConfigManager().setFloat('Configuration/CAMERA_SENSOR_COEF', sensorCoef, 1)

    sensorCoef = property(__getSensorCoef, __setSensorCoef)

    def __getSensorRatio(self):
        """
        """
        return ConfigManager().get('Configuration/CAMERA_SENSOR_RATIO')

    def __setSensorRatio(self, sensorRatio):
        """
        """
        ConfigManager().set('Configuration/CAMERA_SENSOR_RATIO', sensorRatio)

    sensorRatio = property(__getSensorRatio, __setSensorRatio)

    def __getSensorResolution(self):
        """
        """
        return ConfigManager().getFloat('Configuration/CAMERA_SENSOR_RESOLUTION')

    def __setSensorResolution(self, resolution):
        """
        """
        ConfigManager().setFloat('Configuration/CAMERA_SENSOR_RESOLUTION', resolution, 1)

    sensorResolution = property(__getSensorResolution, __setSensorResolution)

    def getYawFov(self, cameraOrientation):
        """ Compute the yaw FoV.

        @return: yaw FoV of the image
        @rtype: float
        """
        if cameraOrientation == 'landscape':
            sensorSize = 36.
        elif cameraOrientation == 'portrait':
            sensorSize = 36. / config.SENSOR_RATIOS[self.sensorRatio]
        else:
            raise ValueError("cameraOrientation must be in ('portrait', 'landscape')")
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
        else:
            raise ValueError("cameraOrientation must be in ('portrait', 'landscape')")

        return self.lens.computeFov(sensorSize / self.sensorCoef)

    def getYawSensorResolution(self, cameraOrientation):
        """ Compute the yaw sensor resolution

        @return: yaw sensor resolution (px)
        @rtype: int
        """
        if cameraOrientation == 'landscape':
            sensorResolution = round(math.sqrt(self.sensorResolution * 1e6 * config.SENSOR_RATIOS[self.sensorRatio]))
        elif cameraOrientation == 'portrait':
            sensorResolution = round(math.sqrt(self.sensorResolution * 1e6 / config.SENSOR_RATIOS[self.sensorRatio]))
        else:
            raise ValueError("cameraOrientation must be in ('portrait', 'landscape')")

        return sensorResolution

    def getPitchSensorResolution(self, cameraOrientation):
        """ Compute the pitch sensor resolution

        @return: pitch sensor resolution (px)
        @rtype: int
        """
        if cameraOrientation == 'landscape':
            sensorResolution = round(math.sqrt(self.sensorResolution * 1e6 / config.SENSOR_RATIOS[self.sensorRatio]))
        elif cameraOrientation == 'portrait':
            sensorResolution = round(math.sqrt(self.sensorResolution * 1e6 * config.SENSOR_RATIOS[self.sensorRatio]))
        else:
            raise ValueError("cameraOrientation must be in ('portrait', 'landscape')")

        return sensorResolution

    def shutdown(self):
        """ Cleanly terminate the camera.

        Save values to preferences.
        """
        Logger().trace("Camera.shutdown()")
        self.lens.shutdown()
