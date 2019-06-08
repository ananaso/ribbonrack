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
    QMainWindow,
    QVBoxLayout,
    QWidget
)
from PyQt5.QtCore import (
        Qt
)

from ribbondisplay import RibbonDisplay
from ribbons import Ribbons
from ribbonscraper import RibbonScraper
from ribbonselector import RibbonSelector


class MainWidget(QWidget):
    '''
    Central widget for managing selector, displayer, etc.
    '''
    def __init__(self, branch, ribbons):
        super().__init__()
        self.layout = QVBoxLayout()
        self.display = RibbonDisplay(branch)
        self.selector = RibbonSelector(ribbons)
        self.layout.addWidget(self.display)
        self.layout.addWidget(self.selector)
        self.setLayout(self.layout)
        self.connect_ui()

    def connect_ui(self):
        '''
        Manages all connection to UI elements
        '''
        self.selector.ribbon_added.connect(self.display.add_ribbon)
        self.selector.ribbon_removed.connect(self.display.remove_ribbon)


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
        self.main_widget = MainWidget("USAF", self.ribbons.precedence['USAF'])
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
