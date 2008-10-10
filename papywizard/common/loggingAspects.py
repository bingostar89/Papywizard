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

Logging

Implements
==========

- LoggingAspect
- logMethods
- unlogMethods
- logModule
- unlogModule

@author: Frédéric Mantegazza
@copyright: (C) 2007-2008 Frédéric Mantegazza
@license: CeCILL
"""
__revision__ = "$Id$"

from logilab.aspects.core import AbstractAspect
from logilab.aspects.prototypes import reassign_function_arguments
from logilab.aspects.weaver import weaver

from papywizard.common.helpers import reprStr, prettyFormat
from papywizard.common.loggingServices import Logger


class LoggingAspect(AbstractAspect):
    """ Logging Aspect Class.
    """

    tab = ""

    def __init__(self, cls):
        """ Create and return the logger aspect.

        @param cls: the class or class instance to aspect
        @param method_name: the name of the method to wrap
        """
        AbstractAspect.__init__(self, cls)
        self.__log = Logger()

    def before(self, wobj, context, *args, **kwargs):
        """ Called before the wrapped method.

        Log the input arguments.
        """
        className = reprStr(context['__class__'])
        methodName = context['method_name']
        method = self._get_method(wobj, wobj.__class__, methodName)
        #className = reprStr(method.im_class)
        strLog = LoggingAspect.tab
        strLog += "Calling %s.%s(" % (className, reprStr(methodName))
        call_dict = reassign_function_arguments(method, args, kwargs)
        for key, val in call_dict.items():
            value = prettyFormat(val)
            strLog += "%s=%s, " % (str(key), reprStr(value))
        strLog += ")"
        self.__log.trace(strLog)
        LoggingAspect.tab += "    "

    #def arround(self, wobj, context, *args, **kwargs):
        #""" Called in the wrapped method ???.
        #"""

    def after(self, wobj, context, *args, **kwargs):
        """ Called after the wrapped method.

        Log the return value or the exception raised.
        """
        className = reprStr(context['__class__'])
        methodName = context['method_name']
        method = self._get_method(wobj, wobj.__class__, methodName)
        #className = reprStr(method.im_class)
        returnValue = context['ret_v']
        LoggingAspect.tab = LoggingAspect.tab[:-4]
        strLog = LoggingAspect.tab
        try:
            exception = context['exec_excpt']
            strLog += "%s.%s() raised exception %s" % (className, methodName, reprStr(exception))
        except KeyError:
            value = prettyFormat(returnValue)
            strLog += "%s.%s() returned %r" % (className, methodName, reprStr(value))
        self.__log.trace(strLog)


def logMethods(obj):
    """ Log all methods of the specified object.
    """
    weaver.weave_methods(obj, LoggingAspect)

def unlogMethods(obj):
    """ Unlog all methods of the specified object.
    """
    weaver.unweave_methods(obj, LoggingAspect)

def logModule(module):
    """ Log all methods of the specified module.

    Same as above, but for all methods of a module.
    """
    weaver.weave_module(module, LoggingAspect)

def unlogModule(module):
    """ Unlog all methods of the specified module.
    """
    weaver.unweave_module(module, LoggingAspect)
