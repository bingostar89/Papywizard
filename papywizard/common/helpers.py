# -*- coding: utf-8 -*-

""" Panohead remote control.

License
=======

 - B{Papywizard} (U{http://www.papywizard.org}) is Copyright:
  - (C) 2007-2011 Frédéric Mantegazza

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

- hmsToS
- hmsToS
- hmsAsStrToS
- sToHms
- sToHmsAsStr

@author: Frédéric Mantegazza
@copyright: (C) 2007-2011 Frédéric Mantegazza
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

def hmsToS(h, m, s):
    """ Convert hours, minutes, seconds to seconds.

    @param h: hours
    @type h: int

    @param m: minutes
    @type m: int

    @param s: seconds
    @type s: int

    @return: seconds
    @rtype: int
    """
    return (h * 60 + m) * 60 + s

def hmsAsStrToS(hhmmss):
    """ Convert hh:mm:ss to seconds.

    @param hhmmss: hours, minutes and seconds
    @type hhmmss: str

    @return: seconds
    @rtype: int
    """
    hhmmss = hhmmss.split(':')
    h = int(hhmmss[0])
    m = int(hhmmss[1])
    s = int(hhmmss[2])
    return hmsToS(h, m, s)

def sToHms(s):
    """ Convert seconds to hours, minutes, seconds.

    @param s: seconds
    @type s: int

    @return: hours, minutes, seconds
    @rtype: tuple of int
    """
    if s < 0:
        s = 0
    h = int(s / 3600)
    m = int((s - h * 3600) / 60)
    s -= (h * 3600 + m * 60)
    return h, m, s

def sToHmsAsStr(s):
    """ Convert seconds to hh:mm:ss.

    @param s: seconds
    @type s: int

    @return: hours, minutes, seconds
    @rtype: str
    """
    return "%02d:%02d:%02d" % sToHms(s)
