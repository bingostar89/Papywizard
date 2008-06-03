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

from common import config
from common.loggingServices import Logger


class ConfigDialog(object):
    """ Preference dialog.
    """
    def __init__(self):
        """ Init the object.
        """
        # Set the Glade file
        gladeFile = os.path.join(path, "configDialog.glade")
        self.wTree = gtk.glade.XML(gladeFile) 
        
        # Retreive usefull widgets
        self._retreiveWidgets()
 
    def _retreiveWidgets(self):
        """ Get widgets from widget tree.
        """
        self.configDialog = self.wTree.get_widget("configDialog")
        self.timeValueSpinbutton = self.wTree.get_widget("timeValueSpinbutton")
        self.nbPictsSpinbutton = self.wTree.get_widget("nbPictsSpinbutton")
        self.delaySpinbutton = self.wTree.get_widget("delaySpinbutton")
        self.sensorCoefSpinbutton = self.wTree.get_widget("sensorCoefSpinbutton")
        self.sensorRatioCombobox = self.wTree.get_widget("sensorRatioCombobox")
        self.overlapSpinbutton = self.wTree.get_widget("overlapSpinbutton")
        self.focalSpinbutton = self.wTree.get_widget("focalSpinbutton")
        self.fisheyeCheckbutton = self.wTree.get_widget("fisheyeCheckbutton")
        self.cameraOrientationCombobox = self.wTree.get_widget("cameraOrientationCombobox")
        self.manualShootCheckbutton = self.wTree.get_widget("manualShootCheckbutton")

    def fillWidgets(self, values):
        """ Fill widgets with values.
        """
        self.timeValueSpinbutton.set_value(values['camera']['timeValue'])
        self.nbPictsSpinbutton.set_value(values['camera']['nbPicts'])
        self.delaySpinbutton.set_value(values['shooting']['delay'])
        self.sensorCoefSpinbutton.set_value(values['camera']['sensorCoef'])
        self.sensorRatioCombobox.set_active(config.SENSOR_RATIOS_INDEX[values['camera']['sensorRatio']])
        self.overlapSpinbutton.set_value(values['shooting']['overlap'])
        self.focalSpinbutton.set_value(values['lens']['focal'])
        self.fisheyeCheckbutton.set_active(values['lens']['fisheye'])
        self.cameraOrientationCombobox.set_active(config.CAMERA_ORIENTATION_INDEX[values['shooting']['cameraOrientation']])
