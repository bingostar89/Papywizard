# -*- coding: iso-8859-1 -*-

""" Panohead remote control.

View.

Implements class:

- ConfigDialog

@author: Frederic Mantegazza
@copyright: 2007
@license: CeCILL
@todo:
"""

__revision__ = "$Id$"

import os.path

#import pygtk
#pygtk.require("2.0")
import gtk.glade

path = os.path.dirname(__file__)

from papywizard.common import config
from papywizard.common.loggingServices import Logger


class ConfigDialog(object):
    """ Preference dialog.
    """
    def __init__(self):
        """ Init the object.
        """
        # Set the Glade file
        gladeFile = os.path.join(path, "configDialog-new.glade")
        self.wTree = gtk.glade.XML(gladeFile)

        # Retreive usefull widgets
        self._retreiveWidgets()

    def _retreiveWidgets(self):
        """ Get widgets from widget tree.
        """
        self.configDialog = self.wTree.get_widget("configDialog")
        self.timeValueSpinbutton = self.wTree.get_widget("timeValueSpinbutton")
        self.nbPictsSpinbutton = self.wTree.get_widget("nbPictsSpinbutton")
        self.stabilizationDelaySpinbutton = self.wTree.get_widget("stabilizationDelaySpinbutton")
        self.sensorCoefSpinbutton = self.wTree.get_widget("sensorCoefSpinbutton")
        self.sensorRatioCombobox = self.wTree.get_widget("sensorRatioCombobox")
        self.overlapSpinbutton = self.wTree.get_widget("overlapSpinbutton")
        self.focalSpinbutton = self.wTree.get_widget("focalSpinbutton")
        self.fisheyeCheckbutton = self.wTree.get_widget("fisheyeCheckbutton")
        self.cameraOrientationCombobox = self.wTree.get_widget("cameraOrientationCombobox")

    def fillWidgets(self, values):
        """ Fill widgets with values.
        """
        self.timeValueSpinbutton.set_value(values['cameraTimeValue'])
        self.nbPictsSpinbutton.set_value(values['cameraNbPicts'])
        self.stabilizationDelaySpinbutton.set_value(values['shootingStabilizationDelay'])
        self.sensorCoefSpinbutton.set_value(values['cameraSensorCoef'])
        self.sensorRatioCombobox.set_active(config.SENSOR_RATIOS_INDEX[values['cameraSensorRatio']])
        self.overlapSpinbutton.set_value(values['shootingOverlap'])
        self.focalSpinbutton.set_value(values['lensFocal'])
        self.fisheyeCheckbutton.set_active(values['lensFisheye'])
        self.cameraOrientationCombobox.set_active(config.CAMERA_ORIENTATION_INDEX[values['shootingCameraOrientation']])
