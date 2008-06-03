# -*- coding: iso-8859-1 -*-

""" Panohead remote control.

Tests.

@author: Frederic Mantegazza
@copyright: 2007
@license: CeCILL
@todo:
"""
import sys
import time

from common import config
from common.loggingServices import Logger
from hardware.axis import Axis
from hardware.driverFactory import DriverFactory

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