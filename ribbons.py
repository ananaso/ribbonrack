#!/usr/bin/env python3
'''
Storage class to centralize all the information about ribbon precendence and
image location.

Author: Alden Davidson, adavidsno@protonmail.ch
Date: Summer 2019
'''

import collections
import copy
from pathlib import Path
import json


class Ribbons():
    '''
    Manages ribbon information
    '''
    def __init__(self):
        self.branches = set(["USAF", "AFROTC"])
        self.precedence = collections.defaultdict(dict)
        self.info_location = Path('./precedence.json')
        self.image_location = Path('./images/')

    def store_precedence(self):
        '''
        Stores current ribbon precedence information in a pretty JSON file.
        Does not check if there's actual ribbon info in self.precedence.
        '''
        self.info_location.touch()
        if self.precedence:
            jsonable_precedence = dict(self.precedence)
            with self.info_location.open('w') as filepath:
                json.dump(jsonable_precedence, filepath,
                          sort_keys=True, indent=4, separators=(',', ': '))
        else:
            raise RuntimeError(
                "Precedence is empty. Try loading or scraping it instead.")

    def load_precedence(self):
        '''
        Loads ribbon precedence information from a JSON file.
        '''
        try:
            with self.info_location.open('r') as filepath:
                self.precedence = json.load(filepath)
            # convert back into default dict
            self.precedence = collections.defaultdict(dict, self.precedence)
            # convert keys back to ints
            newdict = collections.defaultdict(dict)
            for branch, ribbons in self.precedence.items():
                for precedence in ribbons.keys():
                    newdict[branch][int(precedence)] = \
                        self.precedence[branch][precedence]
            self.precedence = copy.deepcopy(newdict)
        except FileNotFoundError:
            print("Precedence file doesn't exist")
            raise
        except json.decoder.JSONDecodeError:
            print("Issue with JSON file. Try loading or scraping it again.")
            raise
