# -*- coding: iso-8859-1 -*-

""" Panohead remote control.

misc classes.

Implements class:

- GovernedRange

@author: Frederic Mantegazza
@copyright: 2007
@license: CeCILL
@todo:
"""

__revision__ = "$Id$"

import time

from papywizard.common.loggingServices import Logger


class GovernedRange(object):
    """ GovernedRange object.

    Returns a range of floats, where each consecutive number is
    incremented at a speed * time between iterations, rather than
    a set value.
    """
    def __init__(self, start, end=None, speed=1):
        """ Init the object.

        @param low: start of range
        @type low: float

        @param high: end of range
        @type high: float

        @param speed: amount to increment, per second.
        @type speed: float
        """
        self.__speed = speed
        self.__start = start
        self.__end = end
        self.__value = self.__start
        self.__time = time.time()

    def __iter__(self):
        """ Define GovernedRange as an iterator.
        """
        while True:
            yield self.next()

    def next(self):
        """ Return the next value.
        """
        inc = self.__speed * (time.time() - self.__time)
        value = self.__value
        value += inc
        self.__time = time.time()
        if self.__end is not None:
            if value >= self.__end:
                raise StopIteration
        self.__value = value

        return value

