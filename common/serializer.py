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

Graphical toolkit helper

Implements
==========

- Serializer

Usage
=====

This serializer allows threads to serialize events to
be processes by the main trhead.

@author: Frédéric Mantegazza
@copyright: (C) 2007-2008 Frédéric Mantegazza
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
