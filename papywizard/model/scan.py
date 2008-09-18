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

Model

Implements
==========

- Scan

@author: Frédéric Mantegazza
@copyright: (C) 2007-2008 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id: scan.py 307 2008-06-24 06:02:36Z fma $"


class Scan(object):
    """ Scan model.

    Scan is the base object for shooting object.

    >>> scan = Scan()
    >>> for yaw, pitch in scan.iterPositions():
    ...     print yaw, pitch
    """
    def __init__(self):
        """ Init the Scan object.
        """
        super(Scan, self).__init__()

    def iterPositions(self):
        """ Iterate over all (yaw, pitch) positions.
        """
        raise NotImplementedError

    # Properties
    def _getTotalNbPicts(self):
        """ Compute the total number of pictures.
        """
        raise NotImplementedError
    
    def __getTotalNbPicts(self):
        """ Workarround to have totalNbPicts property working in subclasses.
        """
        return self._getTotalNbPicts()

    totalNbPicts = property(__getTotalNbPicts)
    
