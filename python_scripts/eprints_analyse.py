#!/usr/bin/env python
# encoding: utf-8

import pandas as pd
import matplotlib.pyplot as plt

INPUT_METADATA_FILE = 'final_df.csv'

SUBSET_YEARS = [str(e) for e in list(range(2000,2022+1))]

EPSRC = ['Engineering and Physical Sciences Research Council', 'EPSRC']
BBSRC = ['Biotechnology and Biological Sciences Research Council', 'BBSRC']
ESRC = ['Economic and Social Research Council', 'ESRC']
NERC = ['Natural Environment Research Council', 'NERC']
AHRC = ['Arts and Humanities Research Council', 'AHRC']
STFC = ['Science and Technology Facilities Council','STFC']
MRC = ['Medical Research Council', 'MRC']

SUBSET_FUNDERS = [
    'EPSRC',
    'BBSRC',
    'ESRC',
    'NERC',
    'AHRC',
    'STFC',
    'MRC']



def import_csv_to_df(filename):
    """
    Imports a csv file into a Pandas dataframe
    :params: an xls file and a sheetname from that file
    :return: a df
    """

    return pd.read_csv(filename, index_col=0)


def clean_data(df):
    """
    Cleans the date and funder information in the dataframe of search terms and metadata (created in 'generate_analysis_metadata.py')
    :params: df: the dataframe created in 'generate_analysis_metadata.py'
    :return: the dataframe with the date and funder information cleaned 
    """

    # Convert date to a date-friendly format
    df['date'] = pd.to_datetime(df['date'], dayfirst=True, errors='coerce')

    # Add column just for year where we can
    df['date_year'] = df['date'].dt.strftime('%Y')

    # Get subset of years that we want
    df = df[df['date_year'].isin(SUBSET_YEARS)]

    #clean funders
    df['funder'][df['funder'].str.contains('|'.join(EPSRC), na=False)] = 'EPSRC'
    df['funder'][df['funder'].str.contains('|'.join(BBSRC), na=False)] = 'BBSRC'
    df['funder'][df['funder'].str.contains('|'.join(ESRC), na=False)] = 'ESRC'
    df['funder'][df['funder'].str.contains('|'.join(NERC), na=False)] = 'NERC'
    df['funder'][df['funder'].str.contains('|'.join(AHRC), na=False)] = 'AHRC'
    df['funder'][df['funder'].str.contains('|'.join(STFC), na=False)] = 'STFC'
    df['funder'][df['funder'].str.contains('|'.join(MRC), na=False)] = 'MRC'

    df.to_csv('analysis_output/csv/cleaned_data.csv')

    return df

def make_graph_by_search_term(df):
    """
    Creates a table and bar graph of the count of each search term (overall and by year).
    These are saved in the analysis_output directory.
    :params: df: the cleaned metadata dataframe
    :return: nothing. Saves the table as a csv and the graph as a png.
    """

    #make a df of just the terms' columns
    search_term_counts = df.drop(['title', 'abstract','funder','date', 'date_year'], axis=1)

    #for each column sum number of non-empty rows
    search_term_counts_summary = search_term_counts.notnull().sum().sort_values(ascending=False)
    search_term_counts_summary.to_csv('analysis_output/csv/search_term_counts_summary.csv')

    plt.rcParams['figure.figsize'] = (4, 12)        
    plot = search_term_counts_summary.plot(kind='barh')
    plot.set_ylabel('Search Term')
    plot.set_xlabel('Number of Publications')
    plt.savefig('analysis_output/png/search_term_counts_summary.png', bbox_inches = 'tight', dpi=150)

    #group by year and then sum by number of rows not empty
    search_term_counts_by_year = df.drop(['title', 'abstract','funder','date'], axis=1)
    search_term_counts_summary_by_year = search_term_counts_by_year.groupby('date_year').count()
    search_term_counts_summary_by_year.to_csv('analysis_output/csv/search_term_counts_summary_by_year.csv')

    plt.rcParams['figure.figsize'] = (9, 12)
    plot = search_term_counts_summary_by_year.plot(kind='bar', stacked=True)
    plt.legend(bbox_to_anchor=(1.0, 1.0))
    plot.set_ylabel('N')
    plot.set_xlabel('Year')
    plt.savefig('analysis_output/png/search_term_counts_summary_by_year.png', bbox_inches = 'tight', dpi=150)

    
def make_graph_by_year(df):
    """
    Creates a table and bar graph of the number of records per year
    These are saved in the analysis_output directory.
    :params: df: the cleaned metadata dataframe
    :return: nothing. Saves the table as a csv and the graph as a png.
    """

    #create graph by year
    year_df = df.loc[:,['title','date_year']]
    year_grouped_df = year_df.groupby('date_year').count()
    year_grouped_df.columns = ['N']
    year_grouped_df.to_csv('analysis_output/csv/year_grouped_count.csv')

    plt.rcParams['figure.figsize'] = (7,5)
    plot = year_grouped_df.plot(kind='bar', legend=False)
    plot.set_ylabel('Number of Publications')
    plot.set_xlabel('Year of Publication')
    plt.savefig('analysis_output/png/plot_by_year.png', bbox_inches = 'tight', dpi=150)


def make_graph_ukri_only(df, subset_funders):
    """
    Creates a table and bar graph of the number of records per funder.
    These are saved in the analysis_output directory.
    Includes only the subset of funders specified in a list.

    :params: df: the cleaned metadata dataframe.
    :params: subset_funders: a list containing the subset of funders to be included in the analysis.
    :return: nothing. Saves the table as a csv and the graph as a png.
    """
    #create graph by funder (ukri funders only)
    funder_df = df[df["funder"].str.contains('|'.join(subset_funders), na=False)]
    funder_only_df = funder_df.loc[:,['title','funder']]

    funder_grouped_df = funder_only_df.groupby('funder').count()
    funder_grouped_df.columns = ['N']
    funder_grouped_df.to_csv('analysis_output/csv/funder_grouped_count.csv')

    plt.rcParams['figure.figsize'] = (7,5)
    plot = funder_grouped_df.plot(kind='bar', legend=False)
    plot.set_ylabel('Number of Publications')
    plot.set_xlabel('Funder')
    plt.savefig('analysis_output/png/plot_by_funder.png', bbox_inches = 'tight', dpi=150)

def make_graph_ukri_by_year(df, subset_funders):
    """
    Creates a table and bar graph of the number of records per year.
    These are saved in the analysis_output directory.
    Includes only the subset of funders specified in a list.

    :params: df: the cleaned metadata dataframe.
    :params: subset_funders: a list containing the subset of funders to be included in the analysis.
    :return: nothing. Saves the table as a csv and the graph as a png.
    """
    #create graph by year for only ukri funded 
    funder_df = df[df["funder"].str.contains('|'.join(subset_funders), na=False)]
    ukri_only = funder_df.loc[:,['title','date_year']]
    ukri_only_year_grouped_df = ukri_only.groupby('date_year').count()
    ukri_only_year_grouped_df.columns = ['N']
    ukri_only_year_grouped_df.to_csv('analysis_output/csv/ukri_only_year_grouped_count.csv')

    plt.rcParams['figure.figsize'] = (7,5)
    plot = ukri_only_year_grouped_df.plot(kind='bar', legend=False)
    plot.set_ylabel('Number of Publications')
    plot.set_xlabel('Year of Publication')
    plt.savefig('analysis_output/png/ukri_only_plot_by_year.png', bbox_inches = 'tight', dpi=150)

def make_graph_by_year_and_funder(df, subset_funders):
    """
    Creates a table and stacked bar graph of the number of records per funder, per year.
    These are saved in the analysis_output directory.
    Includes only the subset of funders specified in a list.

    :params: df: the cleaned metadata dataframe.
    :params: subset_funders: a list containing the subset of funders to be included in the analysis.
    :return: nothing. Saves the table as a csv and the graph as a png.
    """
    #plot by year grouped by funder
    funder_df = df[df["funder"].str.contains('|'.join(subset_funders), na=False)]
    funder_df= funder_df.loc[:,['title','date_year', 'funder']]
    grouped_by_year_and_funder = funder_df.groupby(['date_year', 'funder']).count().reset_index()
    grouped_by_year_and_funder.columns = ['date_year', 'funder', 'N']
    grouped_by_year_and_funder_wide = pd.pivot(grouped_by_year_and_funder, index='date_year', columns='funder', values='N').fillna(0)
    grouped_by_year_and_funder_wide.to_csv('analysis_output/csv/grouped_by_year_and_funder.csv')

    plt.rcParams['figure.figsize'] = (7,5)
    plot = grouped_by_year_and_funder_wide.plot(kind='bar', stacked=True)
    plot.set_ylabel('Number of Publications')
    plot.set_xlabel('Year of Publication')
    plt.savefig('analysis_output/png/plot_by_year_and_funder.png', bbox_inches = 'tight', dpi=150)


def main():

    # Import the overall eprints software term search metadata and clean it
    df = import_csv_to_df(INPUT_METADATA_FILE)
    df = clean_data(df)

    #make each of the graphs, 
    #saving a table of the graph data as csv and the graph as png
    make_graph_by_search_term(df)

    make_graph_by_year(df)

    make_graph_ukri_only(df, SUBSET_FUNDERS)

    make_graph_ukri_by_year(df, SUBSET_FUNDERS)

    make_graph_by_year_and_funder(df, SUBSET_FUNDERS)

if __name__ == '__main__':
    main()