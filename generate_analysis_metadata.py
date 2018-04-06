#!/usr/bin/env python
# encoding: utf-8

import os
import math
import string
import time
import tarfile

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import urllib.request

from xml.etree import cElementTree as et


INPUT_REPOINFO_FILE = 'eprints-repository-overview.csv'
INPUT_XMLDATA_DIR = '/tmp/eprints-data-xml'
OUTPUT_FILE_PREFIX = 'final_df'

XMLNS = 'http://eprints.org/ep2/data/2.0'

IGNORE_TERMS = ['model', 'regression', 'excel']

XML_EXTRACT_FIELDS = {
    'title': 'ep:title',
    'abstract': 'ep:abstract',
    'funder': 'ep:rioxx2_project_input/ep:item/ep:funder_name',
    'date': 'ep:date',
}


def import_csv_to_df(filename):
    """
    Imports a csv file into a Pandas dataframe
    :params: an xls file and a sheetname from that file
    :return: a df
    """

    return pd.read_csv(filename)


def retrieve_xml_from_url(filename):
    """
    This was copied from Steve Crouch's training set collector repo:
    https://github.com/softwaresaved/training-set-collector

    It's purpose is to retrieve and return a GtR XML document from a given URL source.
    """

    # Initialise
    xml_root = None

    try:
        # Get xml from file
        xml_str = urllib.request.urlopen(filename).read()

        # Some returned xml may contain unicode, so need to ensure it's ascii
        xml_str = xml_str.decode('utf8').encode('ascii', 'replace')
        # Use Elementtree to extract XML
        xml_root = et.fromstring(xml_str)
    # The except part is mainly needed if you're getting the data from the API
    # rather than dragging it in from a file like we're doing in this program
    except (urllib.request.HTTPError, urllib.request.URLError) as err:
        print(filename + ": " + str(err))

    return xml_root


def export_to_csv(df, filename, compress=False):
    """
    Exports a df to a csv file, optionally compressing it as a .tar.gz file
    :params: a df and a location in which to save it
    :return: nothing, saves a csv
    """

    df.to_csv(filename + '.csv', index=True)

    if compress:
        with tarfile.open(filename + '.tar.gz', 'w:gz') as targz:
            targz.add(filename + '.csv')


def build_metadata_dataframe(repo_info):

    df = pd.DataFrame(columns=list(XML_EXTRACT_FIELDS.keys()))

    # Go through each eprints repository directory,
    # analysing each search term file of positive
    # record matches, and extract metadata into our
    # summary dataframe
    # TODO: base repo list on INPUT_REPOINFO_FILE URL column
    for repo_dir in os.listdir(INPUT_XMLDATA_DIR):
        print('Processing ' + repo_dir + '...')

        # Go through each search term file
        repo_path = os.path.join(INPUT_XMLDATA_DIR, repo_dir)
        for term_file in os.listdir(repo_path):
            term_name = os.path.splitext(term_file)[0]

            # Skip if this is a term we don't want to analyse
            if term_name in IGNORE_TERMS:
                    break

            print('  Analysing ' + term_file + '...')

            # Load in the xml term file, and extract all eprints records
            xml_root = retrieve_xml_from_url('file://' + os.path.join(repo_path, term_file))
            term_all_records = xml_root.findall('ep:eprint', {'ep': XMLNS})

            # Go through each record with unique ids, extracting
            # search terms where they are found
            for term_record in term_all_records:

                # Must use unique id across all repos, since likely
                # we'll have duplicate entries with multiple authors
                # from multiple institutions
                id = term_record.find('ep:id_number', {'ep': XMLNS})
                if id is not None:
                    # If row doesn't exist with this id, create it with field metadata
                    if id.text not in df.index:

                        # Extract each field we can find, put into summary dataframe
                        for field_name in XML_EXTRACT_FIELDS:
                            field = term_record.find(XML_EXTRACT_FIELDS[field_name], {'ep': XMLNS})

                            if field is not None:
                                df.loc[id.text, field_name] = field.text

                    # Add the found search term details into this row
                    df.loc[id.text, term_name + '_found'] = term_name

    return df


def main():

    repo_info = import_csv_to_df(INPUT_REPOINFO_FILE)

    df = build_metadata_dataframe(repo_info)

    export_to_csv(df, OUTPUT_FILE_PREFIX, compress=False)



if __name__ == '__main__':
    main()
