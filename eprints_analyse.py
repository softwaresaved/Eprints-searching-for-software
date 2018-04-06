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
INPUT_REPOINFO_FILE = 'eprints-repository-overview.csv'
INPUT_YEARLY_REPOINFO_DIR = 'yearly_repo_data'

OUTPUT_DATA_ROWS = 20
OUTPUT_CSV_DIR = 'analysis_output/csv'
OUTPUT_PNG_DIR = 'analysis_output/png'

SUBSET_YEARS = [str(e) for e in list(range(2000,2017+1))]


def import_csv_to_df(filename):
    """
    Imports a csv file into a Pandas dataframe
    :params: an xls file and a sheetname from that file
    :return: a df
    """

    return pd.read_csv(filename, index_col=0)


def clean_data(df):
    df['date'] = pd.to_datetime(df['date'], dayfirst=True, errors='coerce')

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


def count_unique_occurrences(df, count_col, file):
    col = df[count_col]

    # Generate our count of each unique string
    counts = col.value_counts()

    # Create results dataframe for counts
    cdf = pd.DataFrame(counts)
    cdf.columns = ['count']

    # Sort by index
    cdf = cdf.sort_index()

    return cdf


def add_extracted_year (df):
    df['date_year'] = df['date'].dt.strftime('%Y')

    return df


def create_all_artefact_count():
    df = pd.DataFrame()

    for repo_info_file in os.listdir(INPUT_YEARLY_REPOINFO_DIR):
        print('Merging yearly repo data from ' + repo_info_file + '...')

        yearly_repo_info_df = import_csv_to_df(os.path.join(INPUT_YEARLY_REPOINFO_DIR, repo_info_file))
        df[repo_info_file] = yearly_repo_info_df['artefacts']

    df['total_count'] = df.sum(axis=1)

    export_to_csv(df, os.path.join(OUTPUT_CSV_DIR, 'repo-info-all.csv'))

    return df


def main():

    repo_info_df = import_csv_to_df(INPUT_REPOINFO_FILE)

    # Import the overall eprints software term search metadata
    # and convert date to a date-friendly format
    df = import_csv_to_df(INPUT_METADATA_FILE)
    df = clean_data(df)

    # Merge all total repo artefact counts across all repositories
    yearly_repo_info_df = create_all_artefact_count()

    # Add column just for year where we can
    with_year_df = add_extracted_year(df)

    # Count artifacts by year, extract only those years we want
    yearly_df = count_unique_occurrences(with_year_df, 'date_year', 'artifacts_by_year')

    # Get subset of years that we want
    # this also drops NaT conversions
    yearly_df = yearly_df.loc[SUBSET_YEARS,:]
    yearly_df.index = yearly_df.index.map(int)

    # Extract total sums across all repos, put into our high-level
    # dataframe and use to calculate overall percentages per year
    yearly_df['total_count'] = yearly_repo_info_df['total_count']
    yearly_df['percentage'] = round((yearly_df['count'] / yearly_df['total_count']) * 100, 1)

    export_to_csv(yearly_df, os.path.join(OUTPUT_CSV_DIR, 'artifacts_by_year'))

    # Generate and save a basic bar chart
    chart_df = yearly_df['percentage']
    save_bar_chart(chart_df, '% EPrints software-related artifacts', 'Year', 'artifacts_by_year', percentage=True)

    num_total_records = yearly_repo_info_df['total_count'].sum()
    num_software_records = len(with_year_df)
    print("\nTotal number of records:", num_total_records)
    print("Total number of valid software-related records:", len(with_year_df))
    print("Overall percentage of software-related records;", round((num_software_records/num_total_records)*100, 1))


if __name__ == '__main__':
    main()
