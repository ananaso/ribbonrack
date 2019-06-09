#!/usr/bin/env python3
'''
Lists to select and deselect ribbons to display. Utilizes a subclassed
QListWidgetItem to enable precedence-based sorting.

Author: Alden Davidson, adavidson@protonmail.ch
Date: Summer 2019
'''

from PyQt5.QtWidgets import (
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QWidget
)
from PyQt5.QtCore import (
    pyqtSignal,
    pyqtSlot,
    QItemSelectionModel
)


class RibbonListWidgetItem(QListWidgetItem):
    '''
    Subclass of QListWidgetItem to support sorting ribbons by precedence
    '''
    def __init__(self, ribbon, precedence):
        super().__init__()
        self.setText(ribbon)
        self.precedence = precedence

    def __lt__(self, other):
        return self.precedence < other.precedence

    def __repr__(self):
        typestr = "RibbonListWidgetItem"
        return typestr + "(" + self.text() + "," + str(self.precedence) + ")"


class RibbonListWidget(QListWidget):
    '''
    Subclass of QListWidget to support out-of-focus event handling and emission
    of removed ribbon through PyQt signals.
    '''
    removed_ribbon = pyqtSignal(RibbonListWidgetItem)

    def focusOutEvent(self, event):  # pylint: disable=invalid-name
        '''
        Deselect the currently-selected item if the list loses focus
        '''
        for item in self.selectedItems():
            self.setCurrentItem(item, QItemSelectionModel.Deselect)
        super(RibbonListWidget, self).focusOutEvent(event)

    def remove_current_ribbon(self):
        '''
        Removes currently selected ribbon from the list and emits it.
        '''
        ribbon = self.takeItem(self.currentRow())
        self.removed_ribbon.emit(ribbon)

    @pyqtSlot(RibbonListWidgetItem)
    def add_ribbon(self, ribbon):
        '''
        Slot to add a ribbon to the list.
        '''
        self.addItem(ribbon)


class RibbonSelector(QWidget):
    '''
    Allows the user to select the ribbons they want to display.
    '''
    ribbon_added = pyqtSignal(RibbonListWidgetItem)
    ribbon_removed = pyqtSignal(RibbonListWidgetItem)

    def __init__(self, ribbons):
        super().__init__()
        # initialize the lists
        self.masterlist = RibbonListWidget()
        self.currentlist = RibbonListWidget()
        self.init_lists(ribbons)
        # add components to layout
        self.layout = QHBoxLayout(self)
        self.setLayout(self.layout)
        self.init_ui()
        self.connect_ui()

    def init_ui(self):
        '''
        Helper function to manage all widget placement
        '''
        self.layout.addWidget(self.masterlist)
        self.layout.addWidget(self.currentlist)

    def init_lists(self, ribbons):
        '''
        Enable sorting on both lists and then initialize the masterlist with
        all values from ribbon set.
        '''
        self.masterlist.setSortingEnabled(True)
        self.currentlist.setSortingEnabled(True)
        for precedence, ribbon in ribbons.items():
            self.masterlist.addItem(RibbonListWidgetItem(ribbon, precedence))

    def connect_ui(self):
        '''
        Helper function to manage all connections of UI elements
        '''
        # RibbonSelector
        self.masterlist.removed_ribbon.connect(self.on_ribbon_added)
        self.currentlist.removed_ribbon.connect(self.on_ribbon_removed)
        # masterlist
        self.masterlist.itemDoubleClicked.connect(
            self.masterlist.remove_current_ribbon)
        self.masterlist.removed_ribbon.connect(
            self.currentlist.add_ribbon)
        # currentlist
        self.currentlist.itemDoubleClicked.connect(
            self.currentlist.remove_current_ribbon)
        self.currentlist.removed_ribbon.connect(
            self.masterlist.add_ribbon)

    @pyqtSlot(RibbonListWidgetItem)
    def on_ribbon_added(self, ribbon):
        '''
        Forwards signal externally
        '''
        self.ribbon_added.emit(ribbon)

    @pyqtSlot(RibbonListWidgetItem)
    def on_ribbon_removed(self, ribbon):
        '''
        Forwards signal externally
        '''
        self.ribbon_removed.emit(ribbon)
