# -*- coding: utf-8 -*-

""" Panohead remote control.

License
=======

 - B{Papywizard} (U{http://www.papywizard.org}) is Copyright:
  - (C) 2007-2010 Frédéric Mantegazza

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

Configuration

Implements
==========

- PresetTest
- PresetsTest
- PresetManagerTest

@author: Frédéric Mantegazza
@copyright: (C) 2007-2010 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

import unittest
import sys
import os
sys.path.append(os.pardir)

from papywizard.common.presetManager import Preset, Presets, PresetManager

class PresetTest(unittest.TestCase):
    """ Test the Preset class.
    """
    def setUp(self):
        """ Build context (before each xxxTest() method call)
        """

    def tearDown(self):
        """ Cleanup contaxt ((before each xxxTest() method call)
        """


class PresetsTest(unittest.TestCase):
    """ Test the Presets class.
    """
    def setUp(self):
        """ Build context (before each xxxTest() method call)
        """

    def tearDown(self):
        """ Cleanup contaxt ((before each xxxTest() method call)
        """


class PresetManagerTest(unittest.TestCase):
    """ Test the PresetManager class.
    """
    __presets = PresetManager().getPresets()

    def setUp(self):
        """ Build context (before each xxxTest() method call)
        """

    def tearDown(self):
        """ Cleanup contaxt ((before each xxxTest() method call)
        """

    def testAll(self):
        for preset in PresetManagerTest.__presets.getAll():
            print preset
            for yaw, pitch in preset.iterPositions():
                print "yaw=%5.1f, pitch=%5.1f" % (yaw, pitch)


if __name__ == '__main__':
    unittest.main()
