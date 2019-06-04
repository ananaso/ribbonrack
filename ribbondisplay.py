#!/usr/bin/env python3
'''
Manages the display of ribbons in order of precedence. Selects images based
upon data from the currentlist in RibbonSelector

Author: Alden Davidson, adavidson@protonmail.ch
Date: Summer 2019
'''

from pathlib import Path

from PyQt5.QtWidgets import (
    QGridLayout,
    QLabel,
    QWidget
)
from PyQt5.QtGui import (
    QPixmap
)

from ribbons import Ribbons


class RibbonDisplay(QWidget):
    '''
    Displays the ribbons based on what was selected.
    '''
    def __init__(self, branch):
        super().__init__()
        self.branch = branch
        self.layout = QGridLayout(self)
        self.setLayout(self.layout)

    def add_ribbon(self, ribbon):
        '''
        Adds a ribbon to the layout for display
        '''
        cell = QLabel()
        image_path = self.create_image_path(ribbon)
        image = QPixmap(str(image_path))
        cell.setPixmap(image)
        self.layout.addWidget(cell)

    def create_image_path(self, ribbon):
        '''
        Constructs a proper filepath based on branch
        '''
        filename = ribbon.text()
        filename = filename.replace(" ", "")
        if self.branch == 'USAF':
            filename.replace("'", "")
        elif self.branch == 'AFROTC':
            filename.replace("/", "")
        basepath = Ribbons().image_location
        filepath = Path(self.branch + "/" + filename + ".jpeg")
        return basepath.joinpath(filepath)
