# Eprints-searching-for-software
Investigation of EPrints to see whether it can be used to identify software use in papers.

## Important points
Licence for the code and data can be found in the LICENSE file.
The code runs on Perl.
The metadata about the repositories has been sourced from OpenDoar. The data retrieved by the Perl scripts has been sourced from a range of EPrints repositories.

## Summary of Process
* Identify a number of EPrints repositories to investigate.
* Perform a full text searches across these repositories for each term that may be used to identify software use in papers.
* Download publicly available PDFs identified by the search results.

## How to reproduce the results of this analysis
### Set Up
1. Clone this Git repository: https://github.com/softwaresaved/Eprints-searching-for-software.git

2. Install Perl

Required libraries:
* XML::Simple;
* XML::Parser::PerlSAX;
* XML::LibXML;
* Data::Dumper;


3. Identify a list of repository domains and a set of terms you want to search by.

4. Search identified repositories using the search terms.

The 'search_all_terms' Bash script is used to search a given repository for the terms stored in its 'terms' array. 

The script will loop through all the search terms and then for each given repository build a search URL which can be retrieved to provide an XML output of the search.

Search results are downloaded to the 'cache_all' directory, where a subdirectory is created using the repository's domain. A separate XML file for each term is then downloaded to this repository's directory.

Once a term has been searched for and the results downloaded, the script will report the progress and move on to the next term.

'search_all_terms' can be called via 'bash_search_all' Bash script which allows all the repositories to be searched simultaneously and reports when all repository searching is complete.

5. Process the XML Results

'eprints_to_casv_all.pl' loops through all the repositories and all of terms, converting the XML results to a single CSV file, 'all_terms.csv'.

For each repository, it retrieves the XML file for each term, and counts how many results are present. 

Filtering is applied during this counting process so we only count search results which are of type Journal Article or Conference Item.

6. Cross-reference the Results

Because each search term is searched for separately, there may be many cases where the same EPrint is featured in many different results.

We therefore need to cross-reference the results to identify these duplicates.

The 'eprints_crossref.pl' Perl script loops through all the repositories creating a CSV file for each stored in the 'crossreferencing_public' directory, using the repository's domain as the filename.

For each repository, the script loops through all of the terms, loading the XML results for each term in turn.

For each set of search results, the script gets the EPrint IDs used to uniquely identify records in a repository for each record which is either a Journal Article of Conference Item, and where the full text is publicly available.

The EPrint IDs for all the search terms are stored in a hash map, mapping IDs to terms. A download link for the full text is also stored for each EPrint ID.

The script then iterates over the hash map, printing the CSV of the EPrint ID, download URL, a 1 or a 0 for each term to indicate if the term is present, and a final column showing the total number of different terms found.

7. Download PDFs

Once the cross-referencing process has been carried out, we have a list of distinct URLs of publicly available documents to download.

The 'eprints_download.pl' script receives a repository domain as a parameter which it then uses this to read the corresponding cross-reference CSV file.

For each line in the CSV file the script retrieves the EPrint ID and download URL.

The file is then downloaded to the 'pdfs' directory and the corresponding repository subdirectory using the EPrint ID as the filename.

The script then waits for a random amount of time between 5 and 10 seconds to download the next PDF so as not to overload the repository server with requests.

'eprints_download.pl' can be called from 'bash_download' to download from all repositories simultaneously.

## Other Useful Details

### opendoar_to_csv.pl
This was used during the initial identification of EPrints repositories phased. 

It converts XML returned via the OpenDOAR API into a CSV containing details about the repositories.

### get_schema
A Bash script for retrieving a repository's schema. Once retrieved this can be used to convert some of the values in the search result XML files into more meaningful data.

E.g. Convert the code returned for which 'division' an EPrint belongs to, in to the name of the School at that institution.


