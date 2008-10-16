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

@todo: move Merlin/Orion stuff in hardsare module
"""

__revision__ = "$Id$"

from pprint import PrettyPrinter

from papywizard.common import config


def reprStr(obj):
    """ Return a simple name for the object instance.

    <function myFunc at 0x405b1a3c>                                                     -> myFunc
    <class 'module1.module2.MyClass'>                                                   -> myClass
    <class 'module1.module2.MyClass' at 0x408cd3ec>                                     -> MyClass
    <unbound method MyClass.myMethod>                                                   -> myMethod
    <bound method MyClass.myMethod of <module1.module2.MyClass instance at 0x40585e0c>> -> myMethod
    <module1.module2.MyClass instance at 0x40585e2c>                                    -> MyClass at 0x40585e2c
    <module1.module2.MyClass object at 0x40585e2c>                                      -> MyClass at 0x40585e2c
    """
    reprObj = repr(obj)
    reprObj = reprObj.replace("'", "")
    reprObj = reprObj.replace("<", "")
    reprObj = reprObj.replace(">", "")

    if reprObj.find("class") != -1:
        fields = reprObj.split()
        strValue = fields[1].split('.')[-1]

    elif reprObj.find("unbound method") != -1:
        fields = reprObj.split()
        strValue = fields[2].split('.')[-1]

    elif reprObj.find("bound method") != -1:
        fields = reprObj.split()
        strValue = fields[2].split('.')[-1]

    elif reprObj.find("function") != -1:
        fields = reprObj.split()
        strValue = fields[1]

    elif reprObj.find("instance") != -1:
        fields = reprObj.split()
        strValue = "%s at %s" % (fields[0].split('.')[-1], fields[-1])

    elif reprObj.find("object") != -1:
        fields = reprObj.split()
        strValue = "%s at %s" % (fields[0].split('.')[-1], fields[-1])

    else:
        strValue = reprObj

    #reprList = strValue.split()
    #for iPos in xrange(len(reprList)):

        ## Default repr for classes
        #if reprList[iPos] == "<class":
            #strValue = reprList[iPos+1].split(".")[-1][:-2]
            #break

        ## Default repr for methods
        #elif reprList[iPos] == "method":
            #strValue = reprList[iPos+1]
            #break

        ## Default repr for instances
        #elif reprList[iPos] == "object" or reprList[iPos] == "instance":
            #strValue = reprList[iPos-1].split(".")[-1]+" at "+reprList[iPos+2].split(">")[0]
            #break

    return strValue

def prettyFormat(value):
    """ Pretty format a value.

    @param value: value to pretty format
    @type value: python object

    @return: the value pretty formated
    @rtype: str
    """
    pp = PrettyPrinter()
    prettyStr = pp.pformat(value)

    return prettyStr

def isOdd(value):
    """ Test if value is odd.

    @param value: value to test
    @type value: int
    """
    return int(value / 2.) != value / 2.

def decodeAxisValue(strValue):
    """ Decode value from axis.

    Values (position, speed...) returned by axis are
    32bits-encoded strings, low byte first.

    @param strValue: value returned by axis
    @type strValue: str

    @return: value
    @rtype: int

    @todo: put in merlinHelpers?
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

    @todo: put in merlinHelpers?
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

    @todo: put in merlinHelpers?
    """
    return (codPos - config.ENCODER_ZERO) * 360. / config.ENCODER_360

def deg2cod(pos):
    """ Convert degres to encoder value.

    @param pos: position, in °
    @type pos: float

    @return: encoder position
    @rtype: int

    @todo: put in merlinHelpers?
    """
    return int(pos * config.ENCODER_360 / 360. + config.ENCODER_ZERO)

