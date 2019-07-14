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
            USAF="https://www.afpc.af.mil/Recognition/Decorations-and-Ribbons/",  # noqa: E501
            # unofficial source, cannot find official that's scrapeable
            AFROTC="http://patriotfiles.com/forum/showthread.php?t=116789"
        )

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

    def scrape(self, ribbons, branch):
        '''
        Wrapper function to select branch to scrape. Can scrape all if "all"
        is passed in as branch.
        '''
        if any(x is branch for x in ribbons.branches):
            soup = self.get_soup(branch)
            folderpath = Path(
                ribbons.image_location).joinpath(branch + "/")
            folderpath.mkdir(parents=True, exist_ok=True)
            if branch == "USAF":
                print("Scraping USAF at " + self.urls["USAF"])
                self.scrape_usaf(ribbons, soup, folderpath)
            elif branch == "AFROTC":
                print("Scraping AFROTC at " + self.urls["AFROTC"])
                self.scrape_afrotc(ribbons, soup, folderpath)
        elif branch == "all":
            for branches in ribbons.branches:
                self.scrape(ribbons, branches)
        else:
            raise NotImplementedError(
                branch +
                ' is either invalid or unimplemented. Valid options are all, '
                + ribbons.branches)

    def scrape_usaf(self, ribbons, soup, folderpath):
        # pylint: disable=no-self-use
        '''
        Scrapes the information from USAF AFPC ribbons page.
        '''
        rows = soup.find(lambda tag:
                         tag.name == 'div' and
                         tag.has_attr('id') and
                         tag['id'] == "dnn_ctr25862_HtmlModule_lblContent"
                         ).findAll('tr')
        precedence = 0
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
                    ribbon_filename = ribbon_name.replace(" ", "")
                    ribbon_filename = ribbon_filename.replace("'", "")
                    # build filepath to save ribbon image
                    ribbon_filename = Path(
                        ribbon_filename + "." + ribbon_filetype)
                    ribbon_filepath = folderpath.joinpath(ribbon_filename)
                    ribbon_filepath.write_bytes(ribbon_image_data)
                    # put ribbon name into list, in order or precendence
                    ribbons.precedence["USAF"][precedence] = ribbon_name
                    precedence += 1

    def scrape_afrotc(self, ribbons, soup, folderpath):
        # pylint: disable=no-self-use
        '''
        Scrapes information from a forum post listing all AFROTC ribbons.
        '''
        rows = soup.find(lambda tag:
                         tag.name == 'div' and
                         tag.has_attr('id') and
                         tag['id'] == 'post_message_445047'
                         ).table.findAll('tr')
        rows = rows[::2]
        precedence = 0
        for row in rows:
            ribbon_name = row.font.text
            ribbon_name = ribbon_name.replace("*", "")
            ribbon_image_data = requests.get(row.img['src']).content
            # determine actual filetype
            ribbon_filetype = imghdr.what("", ribbon_image_data)
            # create and sanitize filename
            ribbon_name_clean = ribbon_name.replace(" ", "")
            ribbon_name_clean = ribbon_name_clean.replace("/", "")
            ribbon_name_clean = ribbon_name_clean.replace(".", "")
            ribbon_filename = Path(ribbon_name_clean + "." + ribbon_filetype)
            # create full filepath
            ribbon_filepath = folderpath.joinpath(ribbon_filename)
            # save image and ribbon name
            ribbon_filepath.write_bytes(ribbon_image_data)
            ribbons.precedence["AFROTC"][precedence] = ribbon_name
            precedence += 1
