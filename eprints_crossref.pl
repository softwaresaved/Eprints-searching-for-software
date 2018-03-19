#!/usr/bin/perl -w

#Perl script for finding unique EPrint IDs and URLs to documents along with a flag indictaing if a particular search term appears at least once in the document - Will Fyson (2018)

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
"algorithm",
"beautifulsoup",
"code",
"computation",
"computational",
"computed",
"computer",
"database",
"excel",
"fortran",
"gis",
"git",
"github",
"graphics",
"hpc",
"imagej",
"matlab",
"matplotlib",
"model",
"modeling",
"modelling",
"numpy",
"nvivo",
"pipeline",
"python",
"quantitative",
"regression",
"scrapy",
"scipy",
"simulated",
"simulation",
"software",
"spss",
"sqlalchemy",
"stata",
"statistical",
"supercomputing",
"visualisation",
"visualization",
"Rcpp",
"ggplot2",
"plyr",
"stringr",
"reshape2",
"RColorBrewer",
"workflow",
"wxpython",
);

#loop through all the repositories
foreach my $repo( @repositories )
{

	$repo =~ m/https?:\/\/([^\/]+)/; #domain name of repository
	my $repo_url = $1;
	print STDERR "repo_url\n";	

	#generate CSV output
	#prepare file
	my $output = './crossreferencing_public/' . $repo_url . '_crossref.csv';
	open(my $fh, '>', $output) or die "Could not open file '$output' $!";

	#print header row
	my @headers = ( "EPrint ID", "URL" );
	push @headers, @terms;
	push @headers, "Total";
	print $fh join( ',', @headers ). "\n";

	#create an array of eprint ids to term counts
	my %eprintids;

	#read all the xml files in the cache
	my $dir = './cache_all';

	#for each term
	foreach my $term( @terms ) #loop through each term
	{
		print STDERR "term....\n";

		#get the XML
		my $file = "$dir/$repo_url"."/".$term.".xml"; #get the XML

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
				foreach my $eprint ( @{$xpc->findnodes( '/xmlns:eprints/xmlns:eprint', $dom )} ) #loop through all the eprints
				{	
					my $type = $xpc->find('./xmlns:type', $eprint);
					my $full_text_status = $xpc->find('./xmlns:full_text_status', $eprint);
					if( ( $type eq "article" || $type eq "conference_item" ) && $full_text_status eq "public" ) #we're only interested in articles and conference items
					{
						#get the eprint id
						my $id = $xpc->find('./xmlns:eprintid', $eprint);
						$eprintids{$id}{$term} = 1;

						#get the url of the main document
						foreach my $doc ( @{$xpc->findnodes( './xmlns:documents/xmlns:document', $eprint )} )
						{
							my $pos = $xpc->find('./xmlns:pos', $doc );
							if( $pos eq "1" )
							{
								my $url = $xpc->find('./xmlns:main', $doc);
								$eprintids{$id}{url} = "$repo/$id/1/$url" unless defined $eprintids{$id}{url};								
							}
						}
					}
				}
			}
		}	
	}
	
	#print the results, a line for each eprint
	foreach my $eprintid (keys %eprintids)
	{ 
		my @row = ($eprintid, escape_value( $eprintids{$eprintid}{url} ) );
		my $count = 0; #count how many terms appear for the eprint
		foreach my $term( @terms )
		{
			my $termcount = $eprintids{$eprintid}{$term} || 0;
			push @row, $termcount;
			$count = $count + $termcount;
		}
		push @row, $count; #display count at end of row
		print $fh join( ',', @row ) . "\n";
	}

	print STDERR "finished $repo_url \n";
	close $fh;
}
print STDERR "done!!!\n";

sub escape_value
{
        my( $value ) = @_;

        return '""' unless( defined $value );

        # strips any kind of double-quotes:
        $value =~ s/\x93|\x94|"/'/g;
        # and control-characters
        $value =~ s/\n|\r|\t//g;

        # if value is a pure number, then add ="$value" so that Excel stops the auto-formatting (it'd turn 123456 into 1.23e+6)
        if( $value =~ /^[0-9\-]+$/ )
        {
                return "=\"$value\"";
        }

        # only escapes row with spaces and commas
         if( $value =~ /,| / )
        {
                return "\"$value\"";
        }

        return $value;
}
