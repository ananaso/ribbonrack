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
    QHBoxLayout,
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
        self.container_layout = QHBoxLayout()
        self.layout = RibbonGridLayout(self)
        self.container_layout.addStretch()
        self.container_layout.addLayout(self.layout)
        self.container_layout.addStretch()
        self.setLayout(self.container_layout)

    def add_ribbon(self, ribbon):
        '''
        Adds a ribbon to the layout for display
        '''
        # add visible image
        cell = QLabel()
        cell.setAlignment(Qt.AlignCenter)
        image_path = self.create_image_path(ribbon)
        image = QPixmap(str(image_path))
        cell.setPixmap(image)
        ribbon_pair = (ribbon, cell)
        self.layout.add_ribbon(ribbon_pair)
        self.layout.rearrange(ribbon_pair)

    @pyqtSlot(RibbonListWidgetItem)
    def remove_ribbon(self, ribbon):
        '''
        Removes a ribbon from the layout display
        '''
        ribbon_pair, removed_index = self.layout.remove_ribbon(ribbon)
        self.layout.rearrange(ribbon_pair, removed_index)

    def create_image_path(self, ribbon):
        '''
        Constructs a proper filepath based on branch
        '''
        filename = ribbon.text()
        filename = filename.replace(" ", "")
        filename = filename.replace("'", "")
        filename = filename.replace("/", "")
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
        self.setSpacing(0)
        self.setOriginCorner(Qt.BottomRightCorner)
        self.tracker = list()

    def add_ribbon(self, ribbon_pair):
        '''
        Inserts a ribbon into the grid layout and the ribbon tracking list
        '''
        # insert to tracker
        self.tracker.append(ribbon_pair)
        self.tracker.sort(reverse=True)
        # calculate ribbon position
        row, col = divmod(self.tracker.index(ribbon_pair), 3)
        # add to display
        self.addWidget(ribbon_pair[1], row, col)

    def remove_ribbon(self, ribbon_name):
        '''
        Removes a ribbon from the grid layout and the ribbon tracking list
        '''
        # find (ribbon,cell) pair in tracker
        # Must get 0th item since this returns a list containing the tuple
        ribbon_pair = [item for item in self.tracker if ribbon_name in item][0]
        index = self.tracker.index(ribbon_pair)
        # remove parent of cell to destroy it, and stop tracking it
        ribbon_pair[1].setParent(None)
        self.tracker.remove(ribbon_pair)
        return ribbon_pair, index

    def rearrange(self, ribbon_pair, removed_index=None):
        '''
        Rearranges all the ribbons in the display based upon the newly-inserted
        ribbon.
        '''
        max_index = len(self.tracker) - 1
        if removed_index is None:
            new_ribbon_index = self.tracker.index(ribbon_pair)
        else:
            new_ribbon_index = removed_index - 1
        for index in range(max_index, new_ribbon_index, -1):
            # get item from current position
            moving_pair = self.tracker[index]
            moving_pair[1].setParent(None)
            # re-insert item to new position
            row, col = divmod(index, 3)
            self.addWidget(moving_pair[1], row, col)
