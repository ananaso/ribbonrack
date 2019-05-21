#!/usr/bin/env python3
'''
Scrapes USAF AFPC ribbons webpage for images, names, and order.

Author: Alden Davidson, adavidson@protonmail.ch
Date: Summer 2019
'''

import base64
import copy
import imghdr
from pathlib import Path

from bs4 import BeautifulSoup
import requests
from titlecase import titlecase

class RibbonScraper():
    '''
    Scrapes and stores information about ribbons from websites.
    '''
    def __init__(self):
        self.urls = dict(
            USAF="https://www.afpc.af.mil/Recognition/Decorations-and-Ribbons/",
            # using wayback link since this isn't an official source
            AFROTC="https://web.archive.org/web/20150510190040/http://patriotfiles.com/forum/showthread.php?t=116789" # pylint: disable=line-too-long
        )
        self.branches = list(["USA", "USN", "USMC", "USAF", "USCG", "AFROTC"])
        self.ribbons = copy.deepcopy(self.branches)
        self.images_location = Path('./images/USAF')
        self.images_location.mkdir(parents=True, exist_ok=True)

    def get_soup(self, branch):
        '''
        Helper to create the soup for a branch.
        '''
        if branch in self.branches:
            page = requests.get(self.urls[branch])
            soup = BeautifulSoup(page.content, 'lxml')
        else:
            print("Cannot create soup, branch invalid or not implemented.")
            exit()
        return soup

    def scrape(self, branch):
        '''
        Wrapper function to select branch to scrape. Can scrape all
        if "all" is passed in as branch.
        '''
        if any(x is branch for x in self.branches):
            soup = self.get_soup(branch)
            if branch == "USAF":
                self.scrape_usaf(soup)
            elif branch == "AFROTC":
                self.scrape_afrotc(soup)
        elif branch == "all":
            self.scrape_all()
        else:
            print('Invalid branch given. Valid options are "all",' +
                  self.branches)
            exit()

    def scrape_all(self):
        '''
        Wrapper function to scrape all branches in succession.
        '''
        self.scrape_usaf(self.get_soup("USAF"))
        self.scrape_afrotc(self.get_soup("AFROTC"))

    def scrape_usaf(self, soup):
        '''
        Scrapes the information from USAF AFPC ribbons page.
        '''
        rows = soup.find(lambda tag:
                         tag.name == 'div' and
                         tag.has_attr('id') and
                         tag['id'] == "dnn_ctr25862_HtmlModule_lblContent").findAll('tr')
        for row in rows:
            for ribbon in row.findAll('td'):
                ribbon_image_container = ribbon.find('img')
                if ribbon_image_container:
                    # image data is stored directly in HTML as base64 string
                    ribbon_image_data = base64.b64decode(
                        ribbon_image_container['src'].split('base64,', 1)[-1])
                    # determine filetype from image data, since HTML is unreliable
                    ribbon_image_type = imghdr.what("test", ribbon_image_data)
                    # isolate ribbon name
                    ribbon_name = ribbon.find('a').find('span').contents[0]
                    # Some ribbons have title text all screwed up, and can
                    # be detected by checking how many spaces are in string
                    if " " not in ribbon_name:
                        # This alternate location is available for some ribbons
                        ribbon_name = titlecase(ribbon_image_container['alt'].lower())
                    if '(' in ribbon_name:
                        ribbon_name = ribbon_name.split('(')[0].strip()
                    # sanitize name for use as filename
                    ribbon_name_clean = ribbon_name.replace(" ", "")
                    ribbon_name_clean = ribbon_name_clean.replace("'", "")
                    # build filepath to save ribbon image
                    ribbon_filename = Path(ribbon_name_clean + "." + ribbon_image_type)
                    ribbon_filepath = self.images_location.joinpath(ribbon_filename)
                    ribbon_filepath.write_bytes(ribbon_image_data)
                    # put ribbon name into list, in order or precendence
                    self.ribbons.append(ribbon_name)

    def scrape_afrotc(self, soup):
        '''
        Scrapes information from a forum post listing all AFROTC ribbons.
        '''
        rows = soup.find(lambda tag:
                         tag.name == 'div' and
                         tag.has_attr('id') and
                         tag['id'] == 'post_message_445047').table.findAll('tr')
        rows = rows[::2]
        print(rows[0])
        print(rows[1])
        print(rows[2])

if __name__ == "__main__":
    SCRAPER = RibbonScraper()
    SCRAPER.scrape("AFROTC")
