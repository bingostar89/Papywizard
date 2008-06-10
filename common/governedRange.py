# -*- coding: iso-8859-1 -*-

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

Misc

Implements
==========

- GovernedRange

@author: Frédéric Mantegazza
@copyright: (C) 2007-2008 Frédéric Mantegazza
@license: CeCILL
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

