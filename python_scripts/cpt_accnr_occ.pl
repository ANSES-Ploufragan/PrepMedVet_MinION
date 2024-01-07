#!/usr/bin/env perl
use strict;
use warnings;

my $cmd = 'cut -f 2 megablast_out_f_25clmn.tsv | sort';

my @accnr = `$cmd`;
# die "accnr:".join(',', @accnr[0..20])."\n";

my %h_accnr = ();
my $out_f = 'megablast_out_f_25clmn_occ.tsv';

# count accnr
foreach my $accnr(@accnr)
{
    chomp($accnr);
    if(exists $h_accnr{ $accnr }){ $h_accnr{ $accnr }++   }
    else                         { $h_accnr{ $accnr } = 1 }
}

open(my $fh, '>', $out_f)or die "Cannot open $out_f file, line ".__LINE__."\n";

# output each accnr and its number of occurrences in decreasing order 
foreach my $k( sort {$h_accnr{$b} <=> $h_accnr{$a}} keys %h_accnr)
{
    print $fh $k."\t".$h_accnr{$k}."\n";
}
close($fh);
