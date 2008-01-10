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

import config
from loggingServices import Logger
from hardware import Axis, SerialPassiveController


def main1(controller):
    axis = Axis(config.AXIS_NUM_YAW, controller)
    
    # Start test
    axis.init()
    axis.drive(0)
    try:
        startTime = time.time()
    
        for i in xrange(1, 5):
            axis.drive(i * 10)
            print time.time() - startTime, aawAxis.read()
            sys.stdout.flush()
            head.shoot()
        
    except KeyboardInterrupt:
        head.panic()
        
        
def main2(controller):
    axis = Axis(config.AXIS_NUM_YAW, controller)
    
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
        

def main3(controller):
    axis = Axis(config.AXIS_NUM_YAW, controller)
    
    # Start test
    print "Init axis... ",
    sys.stdout.flush()
    axis.init()
    print "Done."
    try:
        print "Drive yaw axis to 45°... ",
        sys.stdout.flush()
        axis.drive(45)
        print "Done."
        print "Drive H axis to 0°... ",
        sys.stdout.flush()
        axis.drive(0)
        print "Done."
    
    except KeyboardInterrupt:
        head.panic()


if __name__ == "__main__":
    controller = SerialPassiveController()
    main1(controller)
    main2(controller)
    main3(controller)
    