#!/usr/bin/env python3
'''
Scrapes ribbons from webpages for images, names, and order.
Sources:
    USAF: AFPC
    AFROTC: PatriotFiles Forum

Author: Alden Davidson, adavidson@protonmail.ch
Date: Summer 2019
'''

import base64
import collections
import imghdr
from pathlib import Path
import pickle

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
            # unofficial source, cannot find official that's scrapeable
            AFROTC="http://patriotfiles.com/forum/showthread.php?t=116789"
        )
        self.branches = set(["USAF", "AFROTC"])
        self.ribbons = collections.defaultdict(set)
        self.images_location = Path('./images/')
        self.info_location = Path('./precendence.p')

    def store_ribbon_precedence(self):
        '''
        Stores the current ribbon precendence information into a pickled file.
        '''
        self.info_location.touch()
        with self.info_location.open('wb') as filepath:
            pickle.dump(self.ribbons, filepath)

    def load_ribbon_precedence(self):
        '''
        Loads the ribbon precedence information from a pickled file.
        Assumes the file exists, please load responsibly.
        '''
        with self.info_location.open('rb') as filepath:
            self.ribbons = pickle.load(filepath)

    def get_soup(self, branch):
        '''
        Helper to create the soup for a branch.
        '''
        url = self.urls[branch]
        page = requests.get(url)
        # check for any 404s (or other errors) before using content
        page.raise_for_status()
        soup = BeautifulSoup(page.content, 'lxml')
        return soup

    def scrape(self, branch):
        '''
        Wrapper function to select branch to scrape. Can scrape all if "all"
        is passed in as branch.
        '''
        if any(x is branch for x in self.branches):
            soup = self.get_soup(branch)
            folderpath = Path(self.images_location).joinpath(branch + "/")
            folderpath.mkdir(parents=True, exist_ok=True)
            if branch == "USAF":
                print("Scraping USAF at " + self.urls["USAF"])
                self.scrape_usaf(soup, folderpath)
            elif branch == "AFROTC":
                print("Scraping AFROTC at " + self.urls["AFROTC"])
                self.scrape_afrotc(soup, folderpath)
        elif branch == "all":
            for branches in self.branches:
                self.scrape(branches)
        else:
            print('Invalid or unimplemented branch given. \
                    Valid options are "all",' + self.branches)
            exit()

    def scrape_usaf(self, soup, folderpath):
        '''
        Scrapes the information from USAF AFPC ribbons page.
        '''
        rows = soup.find(lambda tag:
                         tag.name == 'div' and
                         tag.has_attr('id') and
                         tag['id'] == "dnn_ctr25862_HtmlModule_lblContent"
                         ).findAll('tr')
        for row in rows:
            for ribbon in row.findAll('td'):
                ribbon_image_container = ribbon.find('img')
                if ribbon_image_container:
                    # image data is stored directly in HTML as base64 string
                    ribbon_image_data = base64.b64decode(
                        ribbon_image_container['src'].split('base64,', 1)[-1])
                    # get filetype from image data, since HTML is unreliable
                    ribbon_filetype = imghdr.what("", ribbon_image_data)
                    # isolate ribbon name
                    ribbon_name = ribbon.find('a').find('span').contents[0]
                    # Some ribbons have title text all screwed up, and can
                    # be detected by checking how many spaces are in string
                    if " " not in ribbon_name:
                        # This alternate location is available for some ribbons
                        ribbon_name = titlecase(
                            ribbon_image_container['alt'].lower())
                    if '(' in ribbon_name:
                        ribbon_name = ribbon_name.split('(')[0].strip()
                    # sanitize name for use as filename
                    ribbon_name_clean = ribbon_name.replace(
                        " ", "").replace("'", "")
                    # build filepath to save ribbon image
                    ribbon_filename = Path(
                        ribbon_name_clean + "." + ribbon_filetype)
                    ribbon_filepath = folderpath.joinpath(ribbon_filename)
                    ribbon_filepath.write_bytes(ribbon_image_data)
                    # put ribbon name into list, in order or precendence
                    self.ribbons["USAF"].add(ribbon_name)

    def scrape_afrotc(self, soup, folderpath):
        '''
        Scrapes information from a forum post listing all AFROTC ribbons.
        '''
        rows = soup.find(lambda tag:
                         tag.name == 'div' and
                         tag.has_attr('id') and
                         tag['id'] == 'post_message_445047'
                         ).table.findAll('tr')
        rows = rows[::2]
        for row in rows:
            ribbon_name = row.font.text
            ribbon_image_data = requests.get(row.img['src']).content
            # determine actual filetype
            ribbon_filetype = imghdr.what("", ribbon_image_data)
            # create filename
            ribbon_name_clean = row.font.text.replace(
                " ", "").replace("*", "").replace("/", "")
            ribbon_filename = Path(ribbon_name_clean + "." + ribbon_filetype)
            # create full filepath
            ribbon_filepath = folderpath.joinpath(ribbon_filename)
            # save image and ribbon name
            ribbon_filepath.write_bytes(ribbon_image_data)
            self.ribbons["AFROTC"].add(ribbon_name)


if __name__ == "__main__":
    SCRAPER = RibbonScraper()
    SCRAPER.scrape("AFROTC")
