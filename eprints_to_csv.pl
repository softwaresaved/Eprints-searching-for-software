#!/usr/bin/perl -w

#Perl script for converting XML results from the OpenDOAR API (http://www.opendoar.org/tools/api.html) into a CSV - Will Fyson (2018)

use lib '/root/perl5/lib/perl5';
use XML::Simple;
use XML::Parser::PerlSAX;
use XML::LibXML;
use Data::Dumper;
use strict;

my @repositories = (
"http://publications.aston.ac.uk/",
"http://eprints.cardiff.ac.uk/",
"http://create.canterbury.ac.uk/",
#"http://centaur.reading.ac.uk/",
"http://clok.uclan.ac.uk/",
"http://openaccess.city.ac.uk/",
#"http://dro.dur.ac.uk/",
"https://eprints.soton.ac.uk/",
#"http://www.e-space.mmu.ac.uk/",
#"http://repository.edgehill.ac.uk/",
#"http://eprints.gla.ac.uk/",
"http://repository.falmouth.ac.uk/",
"http://irep.ntu.ac.uk/",
"http://eprints.keele.ac.uk/",
"http://kar.kent.ac.uk/",
"http://eprints.kingston.ac.uk/",
#"http://eprints.lancs.ac.uk/",
"http://researchonline.ljmu.ac.uk/",
"http://eprints.mdx.ac.uk/",
"http://researchonline.ljmu.ac.uk/",
#"http://eprints.mdx.ac.uk/",
"http://eprints.nottingham.ac.uk/",
"http://ray.yorksj.ac.uk/",
"http://researchspace.bathspa.ac.uk/",
"http://roar.uel.ac.uk/",
"http://shura.shu.ac.uk/",
"http://sure.sunderland.ac.uk/",
"http://epubs.surrey.ac.uk/",
"http://sro.sussex.ac.uk/",
#"http://discovery.ucl.ac.uk/",
"http://uir.ulster.ac.uk/",
#"http://epapers.bham.ac.uk/",
#"https://ueaeprints.uea.ac.uk/",
"https://eprints.glos.ac.uk/",
"http://eprints.hud.ac.uk/",
"http://eprints.lincoln.ac.uk/",
"http://usir.salford.ac.uk/",
"https://strathprints.strath.ac.uk/",
"http://eprints.worc.ac.uk/",
#"http://repository.uwl.ac.uk/",
"http://wrap.warwick.ac.uk/",
"http://eprints.whiterose.ac.uk/",
);

my @terms = (
"software",
"program",
"computational",
"HPC",
"simulation",
"modelling",
"visualisation",
"Python",
"Matlab",
"Excel",
"github",
);

#generate CSV output
#prepare file
my $output = './terms.csv';
open(my $fh, '>', $output) or die "Could not open file '$output' $!";

#print header row
my @headers = ( "Repository" );
push @headers, @terms;
print $fh join( ',', @headers ). "\n";

#read all the xml files in the cache
my $dir = './cache';
		
#loop through all the repositories
foreach my $repo( @repositories )
{
	$repo =~ m/https?:\/\/([^\/]+)/; #domain name of repository
	my $repo_url = $1;

	print STDERR "repo_url.....$repo_url\n";

	#print repo domain
	print $fh $repo_url . ",";

	#create array of number of times each term appears (i.e. no. of results in each XML file)
	my @term_counts;
	foreach my $term( @terms ) #loop through each term
	{
		print STDERR "term....$term\n";
		my $count = 0; #reset count
		my $file = "$dir/$repo_url"."_".$term.".xml"; #get the XML

		if( -e $file ) #if XML exists
		{
			print STDERR "xml found\n";
			eval{
				#get parsable XML
				my $dom = XML::LibXML->load_xml( 
					location => $file
				);
				
				my $xpc = XML::LibXML::XPathContext->new;
				$xpc->registerNs('xmlns', 'http://eprints.org/ep2/data/2.0');
				foreach my $eprint ( @{$xpc->findnodes( '/xmlns:eprints/xmlns:eprint', $dom )} )
				{	
					my $type = $xpc->find('./xmlns:type', $eprint);
					if ($type eq "article" || $type eq "conference_item" )
					{
						$count++;
					}
				}
			}
		}	
		push @term_counts, $count; #store results
	}
	print $fh join( ',', @term_counts );
	print $fh "\n";
}
print STDERR "done!!!\n";
close $fh;
