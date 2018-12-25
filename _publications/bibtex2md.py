#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 24 18:39:54 2018

@author: bodo
"""

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This script takes a BibTeX .bib file and outputs a series of .md files for use
in the Academic theme for Hugo, a general-purpose, static-site generating web
framework. Each file incorporates the data for a single publication.

Written for and tested using python 3.6.1

Requires: bibtexparser

Copyright (C) 2017 Mark Coster
"""

import argparse
import os

import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import *


def main():
    #testing
    cd /home/bodo/Dropbox/soft/github/BodoBookhagen.github.io/_publications
    args = parser.parse_args()
    args.bib_file='bookhagen_dec2018.bib'
    args.dir='.'
    args.verbose='true'
    args.selected='true'

    parser = argparse.ArgumentParser()
    parser.add_argument("bib_file", help="BibTeXfile to convert")
    parser.add_argument('dir', nargs='?', default='publication',
                        help="output directory")
    parser.add_argument("-s", "--selected", help="publications 'selected = true'",
                        action="store_true")
    parser.add_argument("-v", "--verbose", help="increase output verbosity",
                        action="store_true")
    args = parser.parse_args()

        with open(args.bib_file) as bib_file:
            bib_data = bibtexparser.load(bib_file)

    if args.verbose:
        print("Verbosity turned on")
        print("Opening {}".format(args.bib_file))

    try:
        with open(args.bib_file) as bib_file:
            #parser = BibTexParser(common_strings=False)
            #parser.customization = customizations
            parser = BibTexParser()
            parser.customization = convert_to_unicode
            bib_data = bibtexparser.load(bib_file, parser=parser)
            #bib_data = bibtexparser.load(bib_file)
    except IOError:
        print('There was a problem opening the file.')

    if not os.path.exists(args.dir):
        if args.verbose:
            print("Creating directory '{}'".format(args.dir))
        os.makedirs(args.dir)
    os.chdir(args.dir)
    paper_number = 0
    bib_data.entries.reverse()
# | Author(s) | Year | Title | Journal | Volume | DOI | 
#Header for table should look like
header = ['---']
header.append("title: Peer-revied journal articles as table list")
header.append('Collection: publications')
header.append('---')
header.append('| Nr. | Author(s) | Year | Title | Journal | Volume/Pages or DOI | ')
header.append('|:---:|:----------|:----:|-------|---------|---------------------|')




    for index, entry in enumerate(bib_data.entries):
        if args.verbose:
            print("Making entry {0}: {1}".format(index + 1, entry['ID']))
        if entry['ENTRYTYPE'] != 'article':
            continue
        paper_number = paper_number + 1
        info = ['---']
        info.append('title: "{}"'.format(entry['title']))
        info.append('collection: publications')
        file_name = entry['year'] + '-' +  entry['ID'] + '-' + str(paper_number) + '.md'
        info.append('permalink: /publication/'+entry['year'] + '-' +  entry['ID'] + '-' + str(paper_number))
        info.append('date: {}-01-01'.format(entry['year']))
        journal_name = entry['journal'].replace('\\', '')
        info.append('venue: "{}"'.format(journal_name))
        if entry['url']:
            info.append('paperurl: "{}"'.format(url))
        if 'abstract' in entry:
            abstract_clean = entry['abstract'].replace('"', '\\"')
            info.append('abstract = "{}"'.format(abstract_clean))
            info.append('abstract_short = "{}"'.format(abstract_clean))
        authors = []
        for author in entry['author'].split(' and '):
            authors.append('"{}"'.format(author))
        info.append('authors = [{}]'.format(', '.join(authors)))
        info.append('image_preview = ""')

        if 'volume' in entry:
            volume = entry['volume'] + ', '
        else:
            volume = ''
        if 'pages' in entry:
            pages = entry['pages'] + ', '
        else:
            pages = ''
        if pages != '' and volume != '':
            info.append('publication_short = "{journal} {year}, {vol}{pages}"'.format(
                journal=journal_name,
                year=entry['year'],
                vol=volume,
                pages=pages))
        else:
            info.append('publication_short = "{journal} {year}"'.format(
                journal=journal_name,
                year=entry['year']))
        info.append('\n---')
        pub_info = '\n'.join(info)

        #write to Markdown table
        header.append('| %02d | %s       '%(paper_number, format(', '.join(authors)))
        try:
            if args.verbose:
                print("Saving '{}'".format(file_name))
            with open(file_name, 'w') as pub_file:
                pub_file.write(pub_info)
        except IOError:
            print('There was a problem writing to the file.')


def customizations(record):
    """Use some functions delivered by the library

    :param record: a record
    :returns: -- customized record
    """
    record = type(record)
    record = author(record)
    record = editor(record)
    record = journal(record)
    record = keyword(record)
    record = link(record)
    record = doi(record)
    record = convert_to_unicode(record)
    record = abstract(record)
    record = pages(record)
    return record


def abstract(record):
    """
    Clean abstract string.

    :param record: a record
    :type record: dict
    :return: dict -- the modified record
    """
    record['abstract'] = record['abstract'].strip(' [on SciFinder(R)]')
    return record


def pages(record):
    """
    Convert double hyphen page range to single hyphen,
    eg. '4703--4705' --> '4703-4705'

    :param record: a record
    :type record: dict
    :return: dict -- the modified record
    """
    record['pages'] = record['pages'].replace('--', '-')
    return record


if __name__ == '__main__':
    main()
    