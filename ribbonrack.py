#!/usr/bin/env python3
'''
Helps build a ribbon rack in the proper order.

Author: Alden Davidson, adavidson@protonmail.ch
Date: Summer 2019
'''

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

from ribbon_scraper import RibbonScraper


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
        self.layout = QVBoxLayout(self)


class MainWidget(QWidget):
    '''
    Central widget for managing selector, displayer, etc.
    '''
    def __init__(self):
        super().__init__()
        pass


class MainWindow(QMainWindow):
    '''
    MainWindow controls display of application.
    '''
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        # window options
        self.setWindowTitle("RibbonRack")
        self.resize(1280, 700)
        self.setCentralWidget(MainWidget)
        self.scraper = RibbonScraper()
        self.init_scraper()

    def init_scraper(self):
        '''
        Initialize the scraper by loading or retrieving precedence info.
        '''
        if self.scraper.info_location.exists():
            self.scraper.load_ribbon_precedence()
        else:
            self.scraper.scrape('all')
            self.store_ribbon_precedence()

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
