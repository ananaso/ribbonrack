#!/usr/bin/env python3
'''
Helps build a ribbon rack in the proper order.

Author: Alden Davidson, adavidson@protonmail.ch
Date: Summer 2019
'''

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
    def __init__(self):
        super().__init__()
        self.layout = QHBoxLayout(self)
        self.master_list = QListWidget()
        self.layout.addWidget(self.master_list)
        self.setLayout(self.layout)


class MainWidget(QWidget):
    '''
    Central widget for managing selector, displayer, etc.
    '''
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.selector = RibbonSelector()
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
        self.mainWidget = MainWidget()
        self.setCentralWidget(self.mainWidget)
        self.scraper = RibbonScraper()
        self.ribbons = Ribbons()
        self.init_ribbons()

    def init_ribbons(self):
        '''
        Initializes ribbon information, and scrapes all if information is not
        already stored.
        '''
        try:
            self.ribbons.load_precedence()
        except FileNotFoundError:
            print("Scraping and storing all ribbons")
            self.scraper.scrape(self.ribbons, 'USAF')
            self.scraper.scrape(self.ribbons, 'AFROTC')
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
