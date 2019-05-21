#!/usr/bin/env python3
'''
Scrapes USAF AFPC ribbons webpage for images, names, and order.

Author: Alden Davidson, adavidson@protonmail.ch
Date: Summer 2019
'''

import base64
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
            USAF_RIBBONS="https://www.afpc.af.mil/Recognition/Decorations-and-Ribbons/"
        )
        self.ribbons = list()
        self.images_location = Path('./images/USAF')
        self.images_location.mkdir(parents=True, exist_ok=True)

    def scrape(self):
        '''
        Scrapes the information from USAF AFPC ribbons page.
        '''
        page = requests.get(self.urls['USAF_RIBBONS'])
        page_data = page.content
        soup = BeautifulSoup(page_data, 'lxml')
        ribbon_table_div = soup.find(lambda tag:
                                     tag.name == 'div' and
                                     tag.has_attr('id') and
                                     tag['id'] == "dnn_ctr25862_HtmlModule_lblContent")
        rows = ribbon_table_div.findAll('tr')
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

if __name__ == "__main__":
    SCRAPER = RibbonScraper()
    SCRAPER.scrape()
