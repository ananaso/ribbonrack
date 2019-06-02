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
        # initialize the lists
        self.masterlist = QListWidget()
        self.init_masterlist(ribbons)
        # add components to layout
        self.layout = QHBoxLayout(self)
        self.layout.addWidget(self.masterlist)
        self.setLayout(self.layout)
        self.connect_ui()

    def init_masterlist(self, ribbons):
        '''
        Initialize the masterlist with all values from ribbon set
        '''
        for ribbon in ribbons.values():
            self.masterlist.addItem(ribbon)

    def connect_ui(self):
        self.masterlist.currentItemChanged.connect(
            lambda: print(self.masterlist.currentItem().text()))


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
