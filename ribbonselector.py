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
    QItemSelectionModel
)


class RibbonSelector(QWidget):
    '''
    Allows the user to select the ribbons they want to display.
    '''
    def __init__(self, ribbons, display):
        super().__init__()
        self.ribbons = ribbons
        self.display = display
        # initialize the lists
        self.masterlist = RibbonListWidget()
        self.currentlist = RibbonListWidget()
        self.masterlist.setSortingEnabled(True)
        self.currentlist.setSortingEnabled(True)
        self.init_masterlist()
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

    def init_masterlist(self):
        '''
        Initialize the masterlist with all values from ribbon set
        '''
        for precedence, ribbon in self.ribbons.items():
            self.masterlist.addItem(RibbonListWidgetItem(ribbon, precedence))

    def connect_ui(self):
        '''
        Helper function to manage all connections of UI elements
        '''
        #self.masterlist.pressed.connect(
        #    lambda: self.currentlist.setCurrentItem(
        #        self.currentlist.currentItem(), QItemSelectionModel.Deselect))
        #self.currentlist.pressed.connect(
        #    lambda: self.masterlist.setCurrentItem(
        #        self.masterlist.currentItem(), QItemSelectionModel.Deselect))
        self.masterlist.itemDoubleClicked.connect(
            self.add_current_item)
        self.currentlist.itemDoubleClicked.connect(
            self.del_current_item)

    def add_current_item(self):
        '''
        Wrapper function to move an item from masterlist to currentlist
        '''
        ribbon = self.masterlist.takeItem(self.masterlist.currentRow())
        self.currentlist.addItem(ribbon)
        self.display.add_ribbon(ribbon)

    def del_current_item(self):
        '''
        Wrapper function to move an item from currentlist back to masterlist
        '''
        ribbon = self.currentlist.takeItem(self.currentlist.currentRow())
        self.masterlist.addItem(ribbon)


class RibbonListWidget(QListWidget):
    '''
    Subclass of QListWidget to support out-of-focus event handling
    '''
    def focusOutEvent(self, event):  # pylint: disable=invalid-name
        '''
        Deselect the currently-selected item if the list loses focus
        '''
        self.setCurrentItem(self.currentItem(), QItemSelectionModel.Deselect)
        super(RibbonListWidget, self).focusOutEvent(event)


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

    def __gt__(self, other):
        return self.precedence > other.precedence
