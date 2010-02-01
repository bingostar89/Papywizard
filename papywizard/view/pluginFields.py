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

Plugins architecture

Implements
==========

- ComboBoxField
- LineEditField
- SpinBoxField
- CheckBoxField

@author: Frédéric Mantegazza
@copyright: (C) 2007-2010 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

from PyQt4 import QtGui, QtCore

from papywizard.common.loggingServices import Logger

LINEEDIT_MINIMUM_WIDTH = 150  # pixels


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
        self.setMinimumWidth(LINEEDIT_MINIMUM_WIDTH)
        self.adjustSize()

    def setValue(self, value):
        self.setText(value)

    def value(self):
        return self.text()


class SpinBoxField(QtGui.QSpinBox):
    """
    """
    def __init__(self, minimum, maximum, prefix="", suffix=""):
        """
        """
        QtGui.QSpinBox.__init__(self)
        self.setAccelerated(True)
        self.setMinimum(minimum)
        self.setMaximum(maximum)
        self.setPrefix(prefix)
        self.setSuffix(suffix)


class DoubleSpinBoxField(QtGui.QDoubleSpinBox):
    """
    """
    def __init__(self, minimum, maximum, decimals=1, singleStep=0.1, prefix="", suffix=""):
        """
        """
        QtGui.QDoubleSpinBox.__init__(self)
        self.setAccelerated(True)
        self.setMinimum(minimum)
        self.setMaximum(maximum)
        self.setDecimals(decimals)
        self.setSingleStep(singleStep)
        self.setPrefix(prefix)
        self.setSuffix(suffix)


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


class ListField(QtGui.QListWidget):
    """
    """
    def __init__(self, entries, select='single'):
        """
        """
        QtGui.QListWidget.__init__(self)
        self.__entries = entries
        self.addItems(entries)
        if select == 'single':
            self.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        elif select == 'contiguous':
            self.setSelectionMode(QtGui.QAbstractItemView.ContiguousSelection)
        elif select == 'extended':
            self.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        elif select == 'multi':
            self.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
        elif select == 'no':
            self.setSelectionMode(QtGui.QAbstractItemView.NoSelection)

    def setValue(self, values):
        self.setCurrentRow(-1)  #, QtGui.QItemSelectionModel.SelectionFlags(QtGui.QItemSelectionModel.Clear))
        for value in values:
            try:
                index = self.__entries.index(value)
            except ValueError:
                Logger().exception("ListField.setValue()", debug=True)
            else:
                self.setCurrentRow(index, QtGui.QItemSelectionModel.SelectionFlags(QtGui.QItemSelectionModel.Select))

    def value(self):
        items = self.selectedItems()
        values = []
        for item in items:
            values.append(unicode(item.text()))
        return values


class DirSelectorField(QtGui.QWidget):
    """
    """
    def __init__(self, title):
        """
        """
        QtGui.QWidget.__init__(self)
        self._title = title

        # Create sub-widgets.
        layout = QtGui.QHBoxLayout(self)
        self._lineEdit = QtGui.QLineEdit(self)
        self._lineEdit.setMinimumWidth(LINEEDIT_MINIMUM_WIDTH)
        layout.addWidget(self._lineEdit)
        self._toolButton = QtGui.QToolButton(self)
        self._toolButton.setText("...")
        layout.addWidget(self._toolButton)

        # Connect signals
        self.connect(self._toolButton, QtCore.SIGNAL("clicked()"), self._onToolButtonClicked)

    def _onToolButtonClicked(self):
        """
        """
        Logger().trace("DirSelectorField.__onToolButtonClicked()")
        dir_ = self._lineEdit.text()
        dirName = QtGui.QFileDialog.getExistingDirectory(self, self._title, dir_, QtGui.QFileDialog.ShowDirsOnly)
        if dirName:
            self._lineEdit.setText(dirName)

    def setValue(self, value):
        self._lineEdit.setText(value)

    def value(self):
        return self._lineEdit.text()


class FileSelectorField(DirSelectorField):
    """
    """
    def __init__(self, title, filter_):
        DirSelectorField.__init__(self, title)
        self.__filter = filter_

    def _onToolButtonClicked(self):
        """
        """
        Logger().trace("FileSelectorField.__onToolButtonClicked()")
        dir_ = self._lineEdit.text()
        fileName = QtGui.QFileDialog.getOpenFileName(self, self._title, dir_, self.__filter)
        if fileName:
            self._lineEdit.setText(fileName)
