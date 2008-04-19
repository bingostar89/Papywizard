# -*- coding: iso-8859-1 -*-

""" Panohead remote control.

This serializer allows threads to serialize events to
be processes by the main trhead.

@author: Frederic Mantegazza
@copyright: 2007
@license: CeCILL
"""

__revision__ = "$Id$"

import sys
import Queue


class Serializer(object):
    """ Events serializer.
    """
    def __init__(self):
        """ Init the serializer
        """
        self.__workRequestQueue = Queue.Queue()
        self.__resultQueue = Queue.Queue()
        
    def apply(self, work, *args, **kwargs):
        """ Add an event to the serializer queue.
        
        @param work: work to push on the queue
        @type work: python callable
        
        Called by an external thread which want to display
        something on the GUI.
        """
        self.__workRequestQueue.put((work, args, kwargs))
        result, exception = self.__resultQueue.get()
        if exception:
            raise exception[0], exception[1], exception[2]
        else:
            return result
    
    def processWork(self):
        """ Execute a queued work.
        
        Called by the main thread to process one
        pending work in the queue.
        """
        try:
            work, args, kwargs = self.__workRequestQueue.get_nowait()
            try:
                result = work(*args, **kwargs)
            except:
                exception = sys.exc_info()
                result = None
            else:
                exception = None
            self.__resultQueue.put((result, exception))
        except Queue.Empty:
            pass
        
        return True
