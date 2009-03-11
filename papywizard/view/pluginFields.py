# -*- coding: utf-8 -*-

""" Panohead remote control.

License
=======

 - B{papywizard} (U{http://trac.gbiloba.org/papywizard}) is Copyright:
  - (C) 2007-2009 Frédéric Mantegazza

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

Plugins architecture

Implements
==========

- ComboBoxField
- LineEditField
- SpinBoxField
- CheckBoxField

@author: Frédéric Mantegazza
@copyright: (C) 2007-2009 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

from PyQt4 import QtGui, QtCore


class ComboBoxField(QtGui.QComboBox):
    """
    """
    def __init__(self, entries):
        """
        """
        QtGui.QComboBox.__init__(self)
        self.addItems(entries)

    def setValue(self, value):
        self.setCurrentIndex(self.findText(value))

    def value(self):
        return self.currentText()


class LineEditField(QtGui.QLineEdit):
    """
    """
    def __init__(self):
        """
        """
        QtGui.QLineEdit.__init__(self)
        self.adjustSize()

    def setValue(self, value):
        self.setText(value)

    def value(self):
        return self.text()


class SpinBoxField(QtGui.QSpinBox):
    """
    """
    def __init__(self, minimum, maximum):
        """
        """
        QtGui.QSpinBox.__init__(self)
        self.setMinimum(minimum)
        self.setMaximum(maximum)


class CheckBoxField(QtGui.QCheckBox):
    """
    """
    def __init__(self):
        """
        """
        QtGui.QCheckBox.__init__(self)

    def setValue(self, value):
        self.setChecked(value)

    def value(self):
        return self.isChecked()


class SliderField(QtGui.QSlider):
    """
    """
    def __init__(self, minimum, maximum, tickInterval=1):
        """
        """
        QtGui.QSlider.__init__(self, QtCore.Qt.Horizontal)
        self.setRange(minimum, maximum)
        self.setTickPosition(QtGui.QSlider.TicksAbove)
        self.setTickInterval(tickInterval)
