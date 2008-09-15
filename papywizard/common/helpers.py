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

Helper functions

Implements
==========

- decodeAxisValue
- encodeAxisValue
- cod2deg
- deg2cod

@author: Frédéric Mantegazza
@copyright: (C) 2007-2008 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

from papywizard.common import config


def decodeAxisValue(strValue):
    """ Decode value from axis.

    Values (position, speed...) returned by axis are
    32bits-encoded strings, low byte first.

    @param strValue: value returned by axis
    @type strValue: str

    @return: value
    @rtype: int
    """
    value = 0
    for i in xrange(3):
        value += eval("0x%s" % strValue[i*2:i*2+2]) * 2 ** (i * 8)

    return value


def encodeAxisValue(value):
    """ Encode value for axis.

    Values (position, speed...) to send to axis must be
    32bits-encoded strings, low byte first.

    @param value: value
    @type value: int

    @return: value to send to axis
    @rtype: str
    """
    strHexValue = "000000%s" % hex(value)[2:]
    strValue = strHexValue[-2:] + strHexValue[-4:-2] + strHexValue[-6:-4]

    return strValue.upper()


def cod2deg(codPos):
    """ Convert encoder value to degres.

    @param codPos: encoder position
    @type codPos: int

    @return: position, in °
    @rtype: float
    """
    return (codPos - config.ENCODER_ZERO) * 360. / config.ENCODER_360


def deg2cod(pos):
    """ Convert degres to encoder value.

    @param pos: position, in °
    @type pos: float

    @return: encoder position
    @rtype: int
    """
    return int(pos * config.ENCODER_360 / 360. + config.ENCODER_ZERO)

