#!/usr/bin/perl -w

#Perl script for converting XML results from the OpenDOAR API (http://www.opendoar.org/tools/api.html) into a CSV - Will Fyson (2018)

use lib '/root/perl5/lib/perl5';
use XML::Simple;
use XML::Parser::PerlSAX;
use Data::Dumper;
use strict;

my $file = "./opendoar.xml"; 

my $xml = XMLin( $file );

#mapping of heading names to field in XML
my %fields = (
	"Name" => "rName",
	"Institution" => "oName",
	"URL" => "rUrl",
	"Items" => "rNumOfItems",
	"Type" => "repositoryType",
	"Status" => "operationalStatus",	
);

#list of policy tpyes in XML
my @policies = ("Policy-Content", "Policy-Preserve", "Policy-Submission", "Policy-Metadata", "Policy-Data");

my @repositories; #store the final results in an array

#print STDERR Dumper( $xml );

#loop through each repository
foreach my $repo( @{$xml->{repositories}->{repository}} )
{	
	if( $repo->{rSoftWareName} eq "EPrints" ) #only interested in EPrints repositories
	{
		#create hash to store repository detials
		my $result = {};

		#loop through the metafields to store key value pairs
		while( my( $field, $value) = each ( %fields ) )
		{
 			$result->{$field} = escape_value( $repo->{$value} );
		}

		#get content types
		$result->{ContentTypes} = join( ';', @{process_array( $repo->{contentTypes}->{contentType} )} );
	
		#get policies
		$result = process_policies( $repo->{policies}->{policy}, $result );

		#add result to array
		push @repositories, $result;
	}
}

#print STDERR Dumper( @repositories );

#generate CSV output
#prepare file
my $output = './repositories.csv';
open(my $fh, '>', $output) or die "Could not open file '$output' $!";

#print header row
my @headers = keys( %fields );
push @headers, 'ContentTypes'; 
push @headers, @policies;
print $fh join( ',', @headers ) . "\n"; 

#loop through all the results!
foreach my $repo( @repositories )
{
	#add values to array for each header
	my @fields;
	foreach my $field( @headers )
	{
		push @fields, $repo->{$field};
	}

	#print the array
	print $fh join( ',', @fields );

	print $fh "\n"; #end of line
}

#finished writing
close $fh;

#get policy data
sub process_policies
{
	my( $policies, $result ) = @_;

	foreach my $policy( @{$policies} )
	{
		#get policy type
		my $policyType = 'Policy-' . $policy->{policyType}->{content};
		
		#get policy content
		my $policy_content;
		if( ref( $policy->{poStandard}->{item} ) eq 'ARRAY' )
		{
			#loop through listed policy items in XML
			my @items;
			foreach my $item( @{$policy->{poStandard}->{item}} )
			{
				if( ref( $item ) ne 'HASH' )
				{
					push @items, $item
				}
			}
			$policy_content = join(" ", @items );
		}
		else #no items defined
		{
			$policy_content = $policy->{poStandard}->{item};
		}
		$result->{$policyType} = escape_value( $policy_content );
	}
	return $result;
}

#for processing an array when multiple values are available (or just a hash which is returned when there is just one value)
sub process_array
{
	my( $array, $node ) = @_;
	my @results;
	if( ref( $array ) eq 'ARRAY' ) #multiple values
	{
		foreach my $value ( @{$array} )
		{
			push @results, escape_value( $value->{content} );			
		}
	}
	else #just a single value...
	{
		push @results, escape_value( $array->{content} );
	}
	return \@results;	
}

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
