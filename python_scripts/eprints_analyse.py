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


INPUT_METADATA_FILE = 'final_df.csv'
INPUT_REPOINFO_FILE = './.data_processing/term_counts/eprints-repository-overview.csv'
INPUT_YEARLY_REPOINFO_DIR = './.data_processing/yearly_repo_data'

OUTPUT_DATA_ROWS = 20
OUTPUT_CSV_DIR = 'analysis_output/csv'
OUTPUT_PNG_DIR = 'analysis_output/png'

SUBSET_YEARS = [str(e) for e in list(range(2000,2017+1))]
SUBSET_FUNDERS = {
    'Engineering and Physical Sciences Research Council': 'EPSRC',
    'Biotechnology and Biological Sciences Research Council': 'BBSRC',
    'Economic and Social Research Council': 'ESRC',
    'Natural Environment Research Council': 'NERC',
    'Arts and Humanities Research Council': 'AHRC',
    'Science and Technology Facilities Council': 'STFC',
    'Medical Research Council': 'MRC',
}


def import_csv_to_df(filename):
    """
    Imports a csv file into a Pandas dataframe
    :params: an xls file and a sheetname from that file
    :return: a df
    """

    return pd.read_csv(filename, index_col=0)


def clean_data(df):
    def clean_funder(input_funder):
        if not isinstance(input_funder, str):
            return ''

        for funder_full, funder_short in SUBSET_FUNDERS.items():
            if funder_full in input_funder or funder_short in input_funder:
                return funder_short

    # Convert date to a date-friendly format
    df['date'] = pd.to_datetime(df['date'], dayfirst=True, errors='coerce')

    # Add column just for year where we can
    df['date_year'] = df['date'].dt.strftime('%Y')

    # Get subset of years that we want
    df = df[df['date_year'].isin(SUBSET_YEARS)]

    # Convert funders to shortened names
    df['funder'] = df['funder'].map(lambda x: clean_funder(x))

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


def save_bar_chart(df, x_col, y_col, file, percentage=False):
    # Must clear the plot first, or labels from previous plots are included
    plt.clf()

    plot = df.plot(kind='bar', legend=False)
    plot.set_xlabel(y_col)
    plot.set_ylabel(x_col)

    # If wanting to display percentage on y axis, set limits accordingly
    if percentage:
        plt.ylim([0, 100])

    fig = plot.get_figure()
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_PNG_DIR, file + '.png'))


def count_unique_occurrences(df, count_col):
    col = df[count_col]

    # Generate our count of each unique string
    counts = col.value_counts()

    # Create results dataframe for counts
    cdf = pd.DataFrame(counts)
    cdf.columns = ['count']

    # Sort by index
    cdf = cdf.sort_index()

    return cdf


def create_all_artefact_count():
    df = pd.DataFrame()

    for repo_info_file in os.listdir(INPUT_YEARLY_REPOINFO_DIR):
        print('Merging yearly repo data from ' + repo_info_file + '...')

        yearly_repo_info_df = import_csv_to_df(os.path.join(INPUT_YEARLY_REPOINFO_DIR, repo_info_file))
        df[repo_info_file] = yearly_repo_info_df['artefacts']

    df['total_count'] = df.sum(axis=1)

    export_to_csv(df, os.path.join(OUTPUT_CSV_DIR, 'repo-info-all.csv'))

    return df


def generate_yearly_software_percentages(df, yearly_repo_info_df):
    # Count artifacts by year, ensure year index is integer for merging
    yearly_df = count_unique_occurrences(df, 'date_year')
    yearly_df.index = yearly_df.index.map(int)

    # Extract total sums across all repos, merge into our high-level
    # dataframe and use to calculate overall percentages per year
    yearly_df['total_count'] = yearly_repo_info_df['total_count']
    yearly_df['percentage'] = round((yearly_df['count'] / yearly_df['total_count']) * 100, 1)

    export_to_csv(yearly_df, os.path.join(OUTPUT_CSV_DIR, 'artifacts_by_year'))

    # Generate and save a basic bar chart
    chart_df = yearly_df['percentage']
    save_bar_chart(chart_df, '% EPrints software-related artifacts', 'Year', 'artifacts_by_year', percentage=True)


def generate_funder_software_percentages(df, yearly_repo_info_df):
    # Get subset of funders that we want
    funder_df = df[df['funder'].isin(SUBSET_FUNDERS.values())]

    # Count artifacts by funder
    funder_df = count_unique_occurrences(funder_df, 'funder')
    funder_df = funder_df.sort_values(by=['count'])

    export_to_csv(funder_df, os.path.join(OUTPUT_CSV_DIR, 'artifacts_by_funder'))

    # Generate and save a basic bar chart
    save_bar_chart(funder_df, '# EPrints software-related artifacts', 'Funder', 'artifacts_by_funder', percentage=False)


def main():

    repo_info_df = import_csv_to_df(INPUT_REPOINFO_FILE)

    # Import the overall eprints software term search metadata and clean it
    df = import_csv_to_df(INPUT_METADATA_FILE)
    df = clean_data(df)

    # Merge all total repo artefact counts across all repositories
    yearly_repo_info_df = create_all_artefact_count()

    # Software-related by year analysis csv and chart
    generate_yearly_software_percentages(df, yearly_repo_info_df)

    # Software-related by funder analysis csv and chart
    generate_funder_software_percentages(df, yearly_repo_info_df)

    num_total_records = yearly_repo_info_df['total_count'].sum()
    num_software_records = len(df)
    print("\nTotal number of records:", num_total_records)
    print("Total number of valid software-related records:", num_software_records)
    print("Overall percentage of software-related records;", round((num_software_records/num_total_records)*100, 1))


if __name__ == '__main__':
    main()
