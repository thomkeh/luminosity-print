#!/usr/bin/python
"""hpmor-scrape.py downloads chapters from hpmor.com.

Each chapter is extracted and saved as an html file.

By default, only missing chapters are downloaded. Run with '--all' to
re-download all chapters.
"""
import os
import os.path
import requests
import re
import time
import random
import argparse
from bs4 import BeautifulSoup

HPMOR_URL = 'http://hpmor.com'
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
OUT_DIR = os.path.join(os.path.split(SCRIPT_DIR)[0], 'html-dump')

def update(all=False):
    """Downloads chapters from hpmor.com.

    Args:
        all (bool): If all is True, re-download all chapters. Otherwise,
            only download missing chapters.
    """
    all_chapters = range(1, newest_chapter()+1)
    if all:
        chapters = all_chapters
    else:
        chapters = set(all_chapters).difference(set(scraped_chapters()))
    download_chapters(chapters, verbose=True)

def newest_chapter():
    """Returns the newest chapter number (int).
    """
    response = requests.get('{}/latest'.format(HPMOR_URL))
    response.raise_for_status()
    return int(response.url.split('/')[-1])

def scraped_chapters():
    """Returns a list of chapters which have already been downloaded.
    """
    chapters = []
    for ch in os.listdir(OUT_DIR):
        match = re.match(r'(\d+).htm', ch)
        if match is not None:
            chapters.append(int(match.group(1)))
    return chapters

def download_chapters(chapters, verbose=False):
    """Downloads chapters and saves as html.
    """
    if verbose:
        n = len(chapters)
        if n == 1:
            print 'downloading {} chapter...'.format(n)
        elif n > 1:
            print 'downloading {} chapters...'.format(n)
        else:
            print 'no chapters to download'
    for ch in chapters:
        url = '{}/chapter/{}'.format(HPMOR_URL, ch)
        if verbose:
            print url
        response = requests.get(url)
        response.raise_for_status()
        response.encoding = 'utf-8'
        html_string = extract_chapter(response.text)
        out_file_path = os.path.join(OUT_DIR,
                                     '{:03d}{}htm'.format(ch, os.extsep))
        with open(out_file_path, 'w') as f:
            f.write(html_string.encode('utf-8'))
        time.sleep(1 + 0.5 * random.random())

def extract_chapter(html_string):
    """Extracts a chapter from an HPMOR webpage.

    Returns the chapter as HTML.
    """
    soup = BeautifulSoup(html_string)
    try:
        chapter_body = soup.find(id='storycontent').extract()
    except:
        raise RuntimeError('No chapter content found')
    chapter_title = soup.title.text
    match = re.match(r'.*Chapter (\d+): (.+)', chapter_title)
    if match is None:
        raise ValueError('Unable to parse chapter title: {}'.format(
                         chapter_title))
    chapter_number = int(match.group(1))
    chapter_title = match.group(2)
    # create a new document and insert chapter body and title
    markup = '<html><head><title>{}</title></head></html>'.format(
                                                    soup.find('title').string)
    document = BeautifulSoup(markup)
    document.head.insert_after(chapter_body)
    title_tag = document.new_tag('h1')
    title_tag.string = chapter_title
    chapter_body.insert_before(title_tag)
    return document.prettify()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Download and extract '
                                     'chapters from hpmor.com')
    parser.add_argument('--all', action='store_true',
                help='download all chapters (default: only missing chapters)')
    args = parser.parse_args()
    update(all=args.all)
