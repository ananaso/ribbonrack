#!/usr/bin/env python3
'''
Helps build a ribbon rack in the proper order.

Author: Alden Davidson, adavidson@protonmail.ch
Date: Summer 2019
'''

import json
import sys

from PyQt5.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QListWidget,
    QMainWindow,
    QVBoxLayout,
    QWidget
)
from PyQt5.QtCore import (
        Qt
)

from ribbonscraper import RibbonScraper
from ribbons import Ribbons


class RibbonDisplay(QWidget):
    '''
    Displays the ribbons based on what was selected.
    '''
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)


class RibbonSelector(QWidget):
    '''
    Allows the user to select the ribbons they want to display.
    '''
    def __init__(self, ribbons):
        super().__init__()
        self.ribbons = ribbons
        # initialize the lists
        self.masterlist = QListWidget()
        self.currentlist = QListWidget()
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
            self.masterlist.insertItem(precedence, ribbon)

    def connect_ui(self):
        '''
        Helper function to manage all connections of UI elements
        '''
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

    def del_current_item(self):
        '''
        Wrapper function to move an item from currentlist back to masterlist
        '''
        ribbon = self.currentlist.takeItem(self.currentlist.currentRow())
        precedence = self.get_precedence(ribbon.text())
        self.masterlist.insertItem(precedence, ribbon)

    def get_precedence(self, ribbon):
        '''
        Helper function to get precedence of a ribbon. Raises KeyError if
        ribbon is not found in list.
        '''
        for precedence, name in self.ribbons.items():
            if ribbon == name:
                return precedence
        raise KeyError(ribbon, "not found in the list!")


class MainWidget(QWidget):
    '''
    Central widget for managing selector, displayer, etc.
    '''
    def __init__(self, ribbons):
        super().__init__()
        self.layout = QVBoxLayout()
        self.selector = RibbonSelector(ribbons)
        self.layout.addWidget(self.selector)
        self.setLayout(self.layout)


class MainWindow(QMainWindow):
    '''
    MainWindow controls display of application.
    '''
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        # window options
        self.setWindowTitle("RibbonRack")
        self.resize(1280, 700)
        # initialize ribbon tools
        self.scraper = RibbonScraper()
        self.ribbons = Ribbons()
        self.init_ribbons()
        # initialize main widget
        self.main_widget = MainWidget(self.ribbons.precedence['USAF'])
        self.setCentralWidget(self.main_widget)

    def init_ribbons(self):
        '''
        Initializes ribbon information, and scrapes all if information is not
        already stored.
        '''
        try:
            self.ribbons.load_precedence()
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            print("Scraping and storing all ribbons")
            self.scraper.scrape(self.ribbons, 'all')
            self.ribbons.store_precedence()
            self.ribbons.load_precedence()

    def keyPressEvent(self, event):  # pylint: disable=invalid-name
        '''
        Defines all custom actions for any keyboard presses. Overrides
        keyPressEvents from MainWindow. This function must be called
        exactly "keyPressEvent" in order to be processed properly by
        PyQt.
        '''
        if event.key() == Qt.Key_Escape:
            self.close()


if __name__ == "__main__":
    APP = QApplication(sys.argv)
    ROOT = MainWindow()
    ROOT.show()
    sys.exit(APP.exec_())
