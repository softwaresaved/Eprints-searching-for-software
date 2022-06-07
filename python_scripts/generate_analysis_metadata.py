# encoding: utf-8

import os
import tarfile
import pandas as pd
import xml.etree.ElementTree as ET

#test_repo_subset = ['clok.uclan.ac.uk', 'eprints.glos.ac.uk']

#ensure that there are not any folders in INPUT_XMLDATA_DIR where all xml files are empty
INPUT_XMLDATA_DIR = './.data_processing/cache_all'

OUTPUT_FILE_PREFIX = 'final_df'

XMLNS = 'http://eprints.org/ep2/data/2.0'

IGNORE_TERMS = ['model', 'regression', 'excel']

XML_EXTRACT_FIELDS = {
    'title': 'ep:title',
    'abstract': 'ep:abstract',
    'funder': 'ep:rioxx2_project_input/ep:item/ep:funder_name',
    'date': 'ep:date',
}



def build_metadata_dataframe(xml_data_directory):
    """
    From a directory of xml files, creates a dataframe of all eprints records.
    The dataframe contains one row per eprints record and one column for each search term 
    as well as columns containing metadata (title, abstract, date, funder).
    :params: xml_data_directory: a directory of folders from each eprints repository,
    with each folder containing one xml file for each search term
    :return: a dataframe of metadata for each eprints record and the search terms 
    in each record
    """
    df = pd.DataFrame(columns=list(XML_EXTRACT_FIELDS.keys()))

    # Go through each eprints repository directory,
    # analysing each search term file of positive
    # record matches, and extract metadata into our
    # summary dataframe
    for repo_dir in os.listdir(xml_data_directory):
        print('Processing ' + repo_dir + '...')

        # Go through each search term file
        repo_path = os.path.join(xml_data_directory, repo_dir)
        for term_file in os.listdir(repo_path):
            term_name = os.path.splitext(term_file)[0]

            # Skip if this is a term we don't want to analyse
            if term_name in IGNORE_TERMS:
                    break

            print('  Analysing ' + term_file + '...')

            # Load in the xml term file, and extract all eprints records
            full_path = os.path.join(repo_path, term_file)

            tree = ET.parse(full_path)
            xml_root = tree.getroot()

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


def main():

    df = build_metadata_dataframe(INPUT_XMLDATA_DIR)

    export_to_csv(df, OUTPUT_FILE_PREFIX, compress=False)


if __name__ == '__main__':
    main()