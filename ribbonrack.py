#!/usr/bin/env python3
'''
Helps build a ribbon rack in the proper order.

Author: Alden Davidson, adavidson@protonmail.ch
Date: Summer 2019
'''

# en.wikipedia.org/wiki/PyQt#PyQt5

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

class RibbonRack(QWidget):
    '''
    RibbonRack widget; contains the actual app content.
    '''
    def __init__(self):
        self.layout = QVBoxLayout(self)


class MainWindow(QMainWindow):
    '''
    MainWindow controls display of application.
    '''
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        # window options
        self.setWindowTitle("RibbonRack")
        self.resize(1280, 700)

    def keyPressEvent(self, event): # pylint: disable=invalid-name
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
