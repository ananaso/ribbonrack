#!/usr/bin/env python3
'''
Storage class to centralize all the information about ribbon precendence and
image location.

Author: Alden Davidson, adavidsno@protonmail.ch
Date: Summer 2019
'''

import collections
from pathlib import Path
import pickle


class Ribbons():
    '''
    Manages ribbon information
    '''
    def __init__(self):
        self.branches = set(["USAF", "AFROTC"])
        self.precedence = collections.defaultdict(set)
        self.info_location = Path('./precedence.p')
        self.image_location = Path('./images/')

    def store_precedence(self):
        '''
        Stores current ribbon precedence information in a pickled file
        '''
        self.info_location.touch()
        with self.info_location.open('wb') as filepath:
            pickle.dump(self.precedence, filepath)

    def load_precedence(self):
        '''
        Loads ribbon precedence information from pickled file.
        '''
        try:
            with self.info_location.open('rb') as filepath:
                self.precedence = pickle.load(filepath)
        except FileNotFoundError:
            print("Precedence pickle doesn't exist")
            raise
