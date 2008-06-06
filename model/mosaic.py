# -*- coding: iso-8859-1 -*-

""" Panohead remote control.

Model.

Implements class:

- Mosaic

@author: Frederic Mantegazza
@copyright: 2007
@license: CeCILL
@todo:
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
    def __init__(self):
        """ Init the Mosaic object.

        Load values from preferences.
        """
        #self.__yawNbPicts = None
        #self.__pitchNbPicts = None
        self.__init = False

        self.template = ConfigManager().get('Preferences', 'MOSAIC_TEMPLATE')

    def __iter__(self):
        """ Define Mosaic as an iterator.
        """
        if self.__yawNbPicts is None or self.__pitchNbPicts is None:
            raise ValueError("You must call setMatrix() first")

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

    def setMatrix(self, yawNbPicts, pitchNbPicts):
        """ Define the number of pictures for both yaw/pitch directions.

        @param yawNbPicts: number of pictures for yaw direction
        @type yawNbPicts: int

        @param pitchNbPicts: number of pictures for pitch direction
        @type pitchNbPicts: int
        """
        self.__yawNbPicts = yawNbPicts
        self.__pitchNbPicts = pitchNbPicts

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
        """ Return next (yaw, pitch) position.
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

    def shutdown(self):
        """ Cleanly terminate the lens

        Save values to preferences.
        """
        Logger().trace("Mosaic.shutdown()")
        ConfigManager().set('Preferences', 'MOSAIC_TEMPLATE', self.template)


def main():
    mosaic = Mosaic()
    mosaic.setMatrix(3, 3)
    for i, (yaw, pitch) in enumerate(mosaic):
        print "pt=%d, yawCoef=%d, pitchCoef=%d" % (i, yaw, pitch)
        

if __name__ == "__main__":
    main()
    