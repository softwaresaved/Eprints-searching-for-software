#!/usr/bin/perl -w

#Perl script for downloading PDFs as listed in the cross referencing CSVs (http://www.opendoar.org/tools/api.html) into a CSV - Will Fyson (2018)

use lib '/root/perl5/lib/perl5';
use strict;

print STDERR $ARGV[0];

my @repositories = (
	$ARGV[0]
);

#loop through all the repositories
foreach my $repo( @repositories )
{

	$repo =~ m/https?:\/\/([^\/]+)/; #domain name of repository
	my $repo_url = $1;
	print STDERR "$repo_url\n";	

	#read all the crossref files
	my $dir = './crossreferencing_public';

	#get the csv
	my $file = "$dir/$repo_url"."_crossref.csv";

	if( -e $file ) #if CSV exists
	{
		print STDERR "csv found\n";

		open(my $data, '<', $file) or die "Could not open '$file' $!\n";
 
		while( my $line = <$data> )
		{
			chomp $line;
 
			#read csv
			my @fields = split "," , $line;
			my $eprintid = $fields[0];
			my $url = $fields[1];
		
			#save pdf according to eprintid
			my $filepath = "./pdfs/$repo_url/$eprintid.pdf";
		
			#only get if we don't have the file already
			if( ! -e $filepath )
			{
				#perform wget
				my $wget = "wget -q -P ./ '$url' -O $filepath";
				system $wget;

				#wait some time before getting the next PDF so as not to concern the server
				my $sleep = 5 + int(rand(10 - 5));
				sleep $sleep;
			}
		}
	}
}

print STDERR "finished..." . $ARGV[0] . "\n";
