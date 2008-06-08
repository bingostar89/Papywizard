# -*- coding: iso-8859-1 -*-

""" Panohead remote control.

Helper functions.

Implements functions:

- decodeAxisValue
- encodeAxisValue
- cod2deg
- deg2cod

@author: Frederic Mantegazza
@copyright: 2007
@license: CeCILL
@todo:
"""

__revision__ = "$Id$"

from papywizard.common.configManager import ConfigManager


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

    @return strValue: value to send to axis
    @rtype strValue: str
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
    encoder_zero = eval(ConfigManager().get('Hardware', 'ENCODER_ZERO'))
    encoder_360 = eval(ConfigManager().get('Hardware', 'ENCODER_360'))
    return (codPos - encoder_zero) * 360. / encoder_360


def deg2cod(pos):
    """ Convert degres to encoder value.

    @param codPos: position, in °
    @type codPos: float

    @return: encoder position
    @rtype: int
    """
    encoder_zero = eval(ConfigManager().get('Hardware', 'ENCODER_ZERO'))
    encoder_360 = eval(ConfigManager().get('Hardware', 'ENCODER_360'))
    return int(pos * encoder_360 / 360. + encoder_zero)

