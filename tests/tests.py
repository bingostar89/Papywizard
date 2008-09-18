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

Unit tests

@author: Frédéric Mantegazza
@copyright: (C) 2007-2008 Frédéric Mantegazza
@license: CeCILL
"""
import sys
import time

from papywizard.common import config
from papywizard.common.loggingServices import Logger
from papywizard.hardware.axis import Axis
from papywizard.hardware.driverFactory import DriverFactory

DRIVER_TYPE = 'bluetooth' # 'serialPassive'


def main1(driver):
    axis = Axis(config.AXIS_NUM_YAW, driver)

    # Start test
    axis.init()
    axis.drive(0)
    try:
        startTime = time.time()

        for i in xrange(1, 5):
            axis.drive(i * 10)
            Logger().debug("%.1f, %.1f" % (time.time() - startTime, aawAxis.read()))
            sys.stdout.flush()
            head.shoot()

    except KeyboardInterrupt:
        head.panic()


def main2(driver):
    axis = Axis(config.AXIS_NUM_YAW, driver)

    # Start test
    axis.init()
    axis.drive(0)
    try:
        head.axis.start(dir=0)
        for i in xrange(5):
            time.sleep(1)
            axis.setOutput(1)
            axis.setOutput(0)
        head.axis.stop()

    except KeyboardInterrupt:
        head.panic()


def main3(driver):
    axis = Axis(config.AXIS_NUM_YAW, driver)

    # Start test
    Logger().debug("Init axis... ")
    axis.init()
    Logger().debug("Done.")
    try:
        Logger().debug("Drive yaw axis to 45°... ")
        axis.drive(45)
        Logger().debug("Done.")
        Logger().debug("Drive pitch axis to 0°... ")
        axis.drive(0)
        Logger().debug("Done.")

    except KeyboardInterrupt:
        head.panic()


def stress(xontroller):
    yawAxis = Axis(config.AXIS_NUM_YAW, driver)
    pitchAxis = Axis(config.AXIS_NUM_PITCH, driver)
    yawAxis.init()
    pitchAxis.init()

    i = 1
    while True:
        Logger().info("Iteration %d" % i)
        Logger().debug("    Drive yaw axis to 10°...")
        yawAxis.drive(10.)
        Logger().debug("    Drive pitch axis to 10°...")
        pitchAxis.drive(10.)
        Logger().debug("    Drive yaw axis to -10°...")
        yawAxis.drive(-10.)
        Logger().debug("    Drive pitch axis to -10°...")
        pitchAxis.drive(-10.)


if __name__ == "__main__":
    driver = DriverFactory().create(DRIVER_TYPE)
    driver.init()
    if DRIVER_TYPE == 'bluetooth':
        time.sleep(8) # wait for the connexion to be really established

    #main1(driver)
    #main2(driver)
    #main3(driver)
    stress(driver)