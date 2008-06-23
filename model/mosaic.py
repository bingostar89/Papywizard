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

Model

Implements
==========

- Mosaic

@author: Frédéric Mantegazza
@copyright: (C) 2007-2008 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

from papywizard.common.loggingServices import Logger
from papywizard.common.configManager import ConfigManager


class Mosaic(object):
    """ Mosaic model.

    This is an iterator which iters of positions to shoot. A
    template defines the way positions are generated.
    Use it just as any iterator:

    >>> mosaic = Mosaic()
    >>> mosaic.template = "Y+P+Y-"
    >>> mosaic.setMatrix(yaw=3, pitch=3)
    >>> for yaw, pitch in mosaic:
    ...     print yaw, pitch
    0 0
    1 0
    2 0
    2 1
    1 1
    0 1
    0 2
    1 2
    2 2
    """
    def __init__(self, yawNbPicts, pitchNbPicts):
        """ Init the Mosaic object.

        @param yawNbPicts: number of pictures for yaw direction
        @type yawNbPicts: int

        @param pitchNbPicts: number of pictures for pitch direction
        @type pitchNbPicts: int
        """
        self.__yawNbPicts = yawNbPicts
        self.__pitchNbPicts = pitchNbPicts

    def __iter__(self):
        """ Define Mosaic as an iterator.
        """

        # Init self.__yaw and self.__pitch according of the template (todo)
        self.__inc = [{'yaw': 1, 'pitch': 0},
                      {'yaw': 0, 'pitch': 1},
                      {'yaw': -1, 'pitch': 0},
                      {'yaw': 0, 'pitch': 1}
                      ]
        self.__start = {'yaw': 0, 'pitch': 0}
        self.__yaw = -1
        self.__yawInc = 1
        self.__pitch = 0
        self.__pitchInc = 1

        return self

    def __getTemplate(self):
        """ Return current used template.
        """
        return ConfigManager().get('Preferences', 'MOSAIC_TEMPLATE')
    
    def __setTemplate(self, template):
        """ Set template to use.
        """
        ConfigManager().set('Preferences', 'MOSAIC_TEMPLATE', template)
        ConfigManager().save()

    template = property(__getTemplate, __setTemplate)

    #def generate(self, yawNbPicts, pitchNbPicts):
        #if not self.__init:
            #inc = [{'yaw': 1, 'pitch': 0},
                   #{'yaw': 0, 'pitch': 1},
                   #{'yaw': -1, 'pitch': 0},
                   #{'yaw': 0, 'pitch': 1}
                  #]
            #yaw = 0
            #pitch = 0
            #idx = 0
            #self.__init = True

        #yield yaw, pitch
        #yaw += inc[idx]['yaw']
        #pitch += inc[idx]['pitch']
        #if yaw >= yawNbPicts:

    def next(self):
        """ Return next (yaw, pitch) index position.
        """
        self.__yaw += self.__yawInc
        if self.__yaw >= self.__yawNbPicts:
            self.__yaw = self.__yawNbPicts - 1
            self.__yawInc = -1
            self.__pitch += self.__pitchInc
            if self.__pitch >= self.__pitchNbPicts:
                self.__yawNbPicts = self.__pitchNbPicts = None
                raise StopIteration
            elif self.__pitch < 0:
                self.__yawNbPicts = self.__pitchNbPicts = None
                raise StopIteration
        elif self.__yaw < 0:
            self.__yaw = 0
            self.__yawInc = +1
            self.__pitch += self.__pitchInc
            if self.__pitch >= self.__pitchNbPicts:
                self.__yawNbPicts = self.__pitchNbPicts = None
                raise StopIteration
            elif self.__pitch < 0:
                self.__yawNbPicts = self.__pitchNbPicts = None
                raise StopIteration
        Logger().debug("Mosaic.next(): __yaw=%d, __pitch=%d" % (self.__yaw, self.__pitch))
        return self.__yaw, self.__pitch


def main():
    mosaic = Mosaic(3, 3)
    for i, (yaw, pitch) in enumerate(mosaic):
        print "pt=%d, yawCoef=%d, pitchCoef=%d" % (i, yaw, pitch)
        

if __name__ == "__main__":
    main()
    