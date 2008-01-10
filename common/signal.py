# -*- coding: iso-8859-1 -*-

""" Panohead remote control.

misc classes.

Implements class:

- Signal
- _WeakMethod_FuncHost
- _WeakMethod

@author: Frederic Mantegazza
@copyright: 2007
@license: CeCILL
@todo:
"""

__revision__ = "$Id$"

import os
import os.path
import weakref
import inspect

from common.loggingServices import Logger


class Signal(object):
    """ class Signal.

    A simple implementation of the Signal/Slot pattern. To use, simply 
    create a Signal instance. The instance may be a member of a class, 
    a global, or a local; it makes no difference what scope it resides 
    within. Connect slots to the signal using the "connect()" method. 
    The slot may be a member of a class or a simple function. If the 
    slot is a member of a class, Signal will automatically detect when
    the method's class instance has been deleted and remove it from 
    its list of connected slots.
    
    This class was generously donated by a poster on ASPN
    see aspn.activestate.com
    """
    def __init__(self):
        """ Init the Signal object.
        """
        self.__slots = []

        # for keeping references to _WeakMethod_FuncHost objects.
        # If we didn't, then the weak references would die for
        # non-method slots that we've created.
        self.__funchost = []

    def __call__(self, *args, **kwargs):
        """ Emit the signal.
        """
        for i in xrange(len(self.__slots)):
            slot = self.__slots[i]
            if slot != None:
                slot(*args, **kwargs)
            else:
                del self.__slots[i]
                
    def emit(self, *args, **kwargs):
        """
        """
        self.__call__(*args, **kwargs)

    def connect(self, slot): # , keepRef=False):
        """
        """
        self.disconnect(slot)
        if inspect.ismethod(slot):
            #if keepRef:
                #self.__slots.append(slot)
            #else:
            self.__slots.append(_WeakMethod(slot))
        else:
            o = _WeakMethod_FuncHost(slot)
            self.__slots.append(_WeakMethod(o.func))
            
            # we stick a copy in here just to keep the instance alive
            self.__funchost.append(o)

    def disconnect(self, slot):
        """
        """
        try:
            for i in xrange(len(self.__slots)):
                wm = self.__slots[i]
                if inspect.ismethod(slot):
                    if wm.f == slot.im_func and wm.c() == slot.im_self:
                        del self.__slots[i]
                        return
                else:
                    if wm.c().hostedFunction == slot:
                        del self.__slots[i]
                        return
        except:
            pass

    def disconnectAll(self):
        """
        """
        del self.__slots
        del self.__funchost
        del self.__methodhost
        self.__slots = []
        self.__funchost = []
        self.__methodhost = []
        

class _WeakMethod_FuncHost:
    """
    """
    def __init__(self, func):
        self.hostedFunction = func
        
    def func(self, *args, **kwargs):
        self.hostedFunction(*args, **kwargs)


class _WeakMethod:
    """
    """
    def __init__(self, f):
        self.f = f.im_func
        self.c = weakref.ref(f.im_self)
        
    def __call__(self, *args, **kwargs):
        if self.c() == None:
            return
        self.f(self.c(), *args, **kwargs)
