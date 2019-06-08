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
from PyQt5.QtCore import (
    pyqtSlot,
    Qt
)

from ribbons import Ribbons
from ribbonselector import RibbonListWidgetItem


class RibbonDisplay(QWidget):
    '''
    Displays the ribbons based on what was selected.
    '''
    def __init__(self, branch):
        super().__init__()
        self.branch = branch
        self.layout = RibbonGridLayout(self)
        self.setLayout(self.layout)

    def add_ribbon(self, ribbon):
        '''
        Adds a ribbon to the layout for display
        '''
        # add visible image
        cell = QLabel()
        image_path = self.create_image_path(ribbon)
        image = QPixmap(str(image_path))
        cell.setPixmap(image)
        self.layout.add_ribbon(ribbon, cell)

    @pyqtSlot(RibbonListWidgetItem)
    def remove_ribbon(self, ribbon):
        '''
        Removes a ribbon from the layout display
        '''
        self.layout.remove_ribbon(ribbon)

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


class RibbonGridLayout(QGridLayout):
    '''
    Custom grid layout for ribbon racks (i.e. 3 ribbon-wide rows) with
    management tools to automate ribbon rearrangement.
    '''
    def __init__(self, parent=None):  # pylint: disable=unused-argument
        super().__init__()
        self.tracker = list()
        self.setOriginCorner(Qt.BottomLeftCorner)

    def add_ribbon(self, ribbon, cell):
        '''
        Inserts a ribbon into the grid layout and the ribbon tracking list
        '''
        # insert to tracker
        item = (ribbon, cell)
        self.tracker.append(item)
        self.tracker.sort()
        self.rearrange(item)
        # add to display
        row, col = divmod(self.tracker.index(item), 3)
        self.addWidget(cell, row, col)

    def remove_ribbon(self, ribbon):
        '''
        Removes a ribbon from the grid layout and the ribbon tracking list
        '''
        # find (ribbon,cell) pair in tracker
        item = [item for item in self.tracker if ribbon in item][0]
        self.tracker.remove(item)
        self.removeWidget(item[1])

    def rearrange(self, item):
        '''
        Rearranges all the ribbons in the display based upon the newly-inserted
        ribbon.
        '''
        max_index = len(self.tracker) - 1
        new_ribbon_index = self.tracker.index(item)
        for index in range(max_index, new_ribbon_index, -1):
            # get item from current position
            moving_item = self.tracker[index][1]
            self.removeWidget(moving_item)
            # re-insert item to new position
            row, col = divmod(index, 3)
            self.addWidget(moving_item, row, col)
