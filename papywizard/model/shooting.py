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

Model

Implements
==========

- Shooting

@author: Frédéric Mantegazza
@copyright: (C) 2007-2008 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

import time
import threading

from papywizard.common import config
from papywizard.common.loggingServices import Logger
from papywizard.common.signal import Signal
from papywizard.common.configManager import ConfigManager
from papywizard.common.exception import HardwareError
from papywizard.model.camera import Camera
from papywizard.model.data import MosaicData, PresetData
from papywizard.model.scan import MosaicScan, PresetScan


class Shooting(object):
    """ Shooting model.
    """
    def __init__(self, realHardware, simulatedHardware):
        """ Init the object.

        @param realHardware: real hardware head
        @type realHardware: {Head}

        @param simulatedHardware: simulated hardware head
        @type simulatedHardware: {HeadSimulation}
        """
        self.__shooting = False
        self.__pause = False
        self.__stop = False
        self.__setParams = None
        self.__manualShoot = False

        self.realHardware = realHardware
        self.simulatedHardware = simulatedHardware
        self.hardware = self.simulatedHardware
        self.switchToRealHardwareSignal = Signal()
        self.newPictSignal = Signal()
        self.startEvent = threading.Event()
        self.startEvent.clear()
        self.camera = Camera()
        self.mosaic = MosaicScan(self)
        self.preset = PresetScan(self)

        self.position = self.hardware.readPosition()
        self.progress = 0.
        self.sequence = _("Idle")

    # Properties
    def __getMode(self):
        return ConfigManager().get('Preferences', 'SHOOTING_MODE')

    def __setMode(self, mode):
        ConfigManager().set('Preferences', 'SHOOTING_MODE', mode)

    mode = property(__getMode, __setMode)

    def __getStabilizationDelay(self):
        return ConfigManager().getFloat('Preferences', 'SHOOTING_STABILIZATION_DELAY')

    def __setStabilizationDelay(self, stabilizationDelay):
        ConfigManager().setFloat('Preferences', 'SHOOTING_STABILIZATION_DELAY', stabilizationDelay, 1)

    stabilizationDelay = property(__getStabilizationDelay, __setStabilizationDelay)

    #def __getheadOrientation(self):
        #"""
        #"""
        #return ConfigManager().getFloat('Preferences', 'SHOOTING_HEAD_ORIENTATION')

    #def __setheadOrientation(self, headOrientation):
        #"""
        #"""
        #ConfigManager().setFloat('Preferences', 'SHOOTING_HEAD_ORIENTATION', headOrientation)

    #headOrientation = property(__getHeadOrientation, __setHeadOrientation)
    headOrientation = 'vertical'

    def __getCameraOrientation(self):
        """
        """
        return ConfigManager().get('Preferences', 'SHOOTING_CAMERA_ORIENTATION')

    def __setCameraOrientation(self, cameraOrientation):
        """
        """
        ConfigManager().set('Preferences', 'SHOOTING_CAMERA_ORIENTATION', cameraOrientation)

    cameraOrientation = property(__getCameraOrientation, __setCameraOrientation)

    #def __getCameraRoll(self):
        #"""
        #"""
        #return ConfigManager().getFloat('Preferences', 'SHOOTING_CAMERA_ROLL')

    #def __setCameraRoll(self, cameraRoll):
        #"""
        #"""
        #ConfigManager().setFloat('Preferences', 'SHOOTING_CAMERA_ROLL', cameraRoll)

    #cameraRoll = property(__getCameraRoll, __setCameraRoll)
    cameraRoll = 60.

    def switchToRealHardware(self):
        """ Use real hardware.
        """
        Logger().trace("Shooting.switchToRealHardware()")
        try:
            #self.simulatedHardware.shutdown()
            self.realHardware.init()
            Logger().debug("Shooting.switchToRealHardware(): realHardware initialized")
            self.position = self.realHardware.readPosition()
            self.hardware = self.realHardware
            self.switchToRealHardwareSignal.emit(True)
        except HardwareError, message:
            Logger().exception("Shooting.switchToRealHardware()")
            self.switchToRealHardwareSignal.emit(False, str(message))

    def switchToSimulatedHardware(self):
        """ Use simulated hardware.
        """
        Logger().trace("Shooting.switchToSimulatedHardware()")
        try:
            self.realHardware.shutdown()
        except:
            Logger().exception("Shooting.switchToSimulatedHardware()")
        self.hardware = self.simulatedHardware
        self.hardware.init()
        self.position = self.hardware.readPosition()

    def setManualShoot(self, flag):
        """ Turn on/off manual shoot.

        In manual shoot mode, the head switch to pause at each end of position.

        @param flag: flag for manual shoot
        @type flag: bool
        """
        self.__manualShoot = flag

    def initProgress(self):
        """ Init progress value.
        """
        self.progress = 0.
        self.sequence = _("Idle") # find better

    def start(self):
        """ Start pano shooting.
        """
        def checkPauseStop():
            """ Check if pause or stop requested.
            """
            if self.__pause:
                Logger().info("Pause")
                self.sequence = _("Idle")
                while self.__pause:
                    time.sleep(0.1)
                Logger().info("Resume")
            if self.__stop:
                Logger().info("Stop")
                raise StopIteration

        Logger().trace("Shooting.start()")

        if self.cameraOrientation == 'portrait':
            roll = 90.
        elif self.cameraOrientation == 'landscape':
            roll = 0.
        elif self.cameraOrientation == 'custom':
            roll = self.cameraRoll
        else:
            raise ValueError("cameraOrientation must be in ('portrait', 'landscape', 'custom'")
        values = {'title' : "Here goes the title",
                  'gps': "Here goes the gps data",
                  'comment': "Generated by Papywizard %s" % config.VERSION,
                  'headOrientation': "up", # up, left, right, down
                  'cameraOrientation': "%s" % self.cameraOrientation, # portrait, landscape or custom
                  'roll': "%.1f" % roll,
                  'stabilizationDelay': "%.1f" % self.stabilizationDelay,
                  'timeValue': "%.1f" % self.camera.timeValue,
                  'bracketingNbPicts': "%d" % self.camera.bracketingNbPicts,
                  'bracketingIntent': "%s" % self.camera.bracketingIntent,
                  'sensorCoef': "%.1f" % self.camera.sensorCoef,
                  'sensorRatio': "%s" % self.camera.sensorRatio,
                  'lensType': "%s" % self.camera.lens.type_,
                  'focal': "%.1f" % self.camera.lens.focal}
        if self.mode == 'mosaic':
            data = MosaicData()
            values.update({'yawNbPicts': "%d" % self.mosaic.yawNbPicts,
                           'pitchNbPicts': "%d" % self.mosaic.pitchNbPicts,
                           'overlap': "%.2f" % self.mosaic.overlap,
                           'yawRealOverlap': "%.2f" % self.mosaic.yawRealOverlap,
                           'pitchRealOverlap': "%.2f" % self.mosaic.pitchRealOverlap})
        else:
            data = PresetData()
            values.update({'name': "%s" % self.preset.name})
        data.createHeader(values)
        self.error = False
        self.progress = 0.
        self.__stop = False
        self.__shooting = True
        self.startEvent.set()

        # Loop over all positions
        if self.mode == 'mosaic':
            scan = self.mosaic
        else:
            scan = self.preset
        try:
            for i, (yaw, pitch) in enumerate(scan.iterPositions()):
                Logger().debug("Shooting.start(): goto yaw=%.1f pitch=%.1f" % (yaw, pitch))
                Logger().info("Moving")
                self.sequence = _("Moving")
                try:
                    self.hardware.gotoPosition(yaw, pitch)

                    checkPauseStop()

                    Logger().info("Stabilization")
                    self.sequence = _("Stabilizing")
                    time.sleep(self.stabilizationDelay)

                    if self.__manualShoot:
                        self.__pause = True
                        Logger().info("Manual shoot")

                    checkPauseStop()

                    Logger().info("Shooting")
                    for bracket in xrange(self.camera.bracketingNbPicts):
                        Logger().debug("Shooting.start(): shooting %d/%d" % (bracket + 1, self.camera.bracketingNbPicts))
                        self.sequence = _("Shooting %d/%d") % (bracket + 1, self.camera.bracketingNbPicts)
                        self.hardware.shoot(self.camera.timeValue)
                        time.sleep(0.5) # ensure shutter is closed()

                        data.addPicture(bracket + 1, yaw, pitch, roll)

                        checkPauseStop()

                    progressFraction = float((i + 1)) / float(scan.totalNbPicts)
                    self.progress = progressFraction
                    self.newPictSignal.emit(yaw, pitch, status='ok') # Include progress?
                    # todo: add status of current picture (to draw it in red if failed to go)

                except HardwareError:
                    self.hardware.stopAxis()
                    Logger().exception("Shooting.start()")
                    Logger().warning("Shooting.start(): position (yaw=%.1f, pitch=%.1f) out of limits" % (yaw, pitch))

                    progressFraction = float((i + 1)) / float(scan.totalNbPicts)
                    self.progress = progressFraction
                    self.newPictSignal.emit(yaw, pitch, status='error') # Include progress?
                    # todo: add status of current picture (to draw it in red if failed to go)

            Logger().debug("Shooting.start(): finished")

        except StopIteration:
            Logger().debug("Shooting.start(): stop detected")
            self.sequence = _("Canceled")
        except:
            Logger().exception("Shooting.start()")
            self.error = True
        else:
            self.sequence = _("Finished")

        self.__shooting = False

    def isShooting(self):
        """ Test if shooting is running.

        @return: True if shooting is running, False otherwise
        @rtype: bool
        """
        return self.__shooting

    def pause(self):
        """ Pause execution of pano shooting.
        """
        Logger().trace("Shooting.pause()")
        self.__pause = True

    def isPaused(self):
        """ Test if shotting is paused.

        @return: True if shooting is paused, False otherwise
        @rtype: bool
        """
        return self.__pause

    def resume(self):
        """ Resume  execution of shooting.
        """
        Logger().trace("Shooting.resume()")
        self.__pause = False

    def stop(self):
        """ Cancel execution of shooting.
        """
        Logger().trace("Shooting.stop()")
        self.__stop = True
        self.__pause = False
        self.hardware.stopAxis()

    def shutdown(self):
        """ Cleanly terminate the model.

        Save values to preferences.
        """
        Logger().trace("Shooting.shutdown()")
        #self.realHardware.shutdown()
        #self.simulatedHardware.shutdown()
        self.hardware.shutdown()
        self.camera.shutdown()
        ConfigManager().save()
