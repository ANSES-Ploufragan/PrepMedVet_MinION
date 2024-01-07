#!/usr/bin/env perl
use warnings;
use strict;

my $prog_tag = '[taxid_assemblyaccnr_2_seqaccnr_taxid]';
my $b_test_get_taxid_4_assemblyaccnr            = 0; # ok 2023 12 21
my $b_test_taxid_assemblyaccnr_2_seqaccnr_taxid = 0; # ok 2023 12 21

# return a hash table key:assemblyaccnr value:taxid:
sub get_taxid_4_assemblyaccnr($$)
{
    my($taxid_assemblyaccnr_f, $r_h_assemblyaccnr_taxid) = @_;

    %$r_h_assemblyaccnr_taxid = ();
    open(my $taf, '<', $taxid_assemblyaccnr_f)or die("$prog_tag [Error] Cannot open $taxid_assemblyaccnr_f file:$!, line ".__LINE__."\n");
    while(<$taf>)
    {
        chomp();
        /^(\d+) (\S+)$/ and do{ $r_h_assemblyaccnr_taxid->{ $2 } = $1 }
    }
    close($taf)
    # return \%h_assemblyaccnr_taxid;
}

if($b_test_get_taxid_4_assemblyaccnr)
{
    my $test_dir = "../taxid_lists/";
    my $taxid_assemblyaccnr_f = $test_dir.'host_complete_genomes_taxid_accnr.tsv';
    my %h_assemblyaccnr_taxid = ();
    get_taxid_4_assemblyaccnr($taxid_assemblyaccnr_f, \%h_assemblyaccnr_taxid);
    print("$prog_tag [TEST][get_taxid_4_assemblyaccnr] START\n");
    while( my($k,$v) = each %h_assemblyaccnr_taxid)
    {
        print("k:$k\tv:$v\n");
    }
    print("$prog_tag [TEST][get_taxid_4_assemblyaccnr] START\n");
    exit();
}

sub taxid_assemblyaccnr_2_seqaccnr_taxid($$$$$)
{
    my( $taxid_assemblyaccnr_f,            # tsv file woth taxid and assembly_accnr for each line
        $r_fna_gz_list,                    # list of fna.gz file of the host_complete_genomes_db
        $out_seqaccnr_taxid_4makeblastdb_f, # out file dedicated to makeblastdb so as to create taxonomic link with accnr
        $out_dir_assemblyaccnr_lists,      # directory where are stored files GCF_dddddddd.d.txt list with seq accession numbers into
        $nb_threads
        ) = @_;

    if($out_dir_assemblyaccnr_lists !~ /\/$/){  $out_dir_assemblyaccnr_lists .= '/' }

    my %h_assemblyaccnr_taxid = ();
    get_taxid_4_assemblyaccnr($taxid_assemblyaccnr_f, \%h_assemblyaccnr_taxid);

    # one file for all acc_nr for makeblastdb
    open(my $st4b, '>', $out_seqaccnr_taxid_4makeblastdb_f)or die("$prog_tag [Error] Cannot create $out_seqaccnr_taxid_4makeblastdb_f file:$!, line ".__LINE__."\n");
    
    my $nb_fna_gz_f = scalar(@$r_fna_gz_list);
    print("$prog_tag $nb_fna_gz_f .fna.gz file founds\n");
    for my $file(@$r_fna_gz_list)
    {
        # check file name, get accession number of the assembly (corresponds to several sequences in the file)
        my $assemblyaccnr = undef;
        if($file =~ /(GCF_[^_]+)_.*?.fna.gz$/){  $assemblyaccnr = $1  }
        else{ die("$prog_tag Error, only accnr_assembly fna.gz files are accepted, line ".__LINE__."\n") }

        # get fasta headers (first accession number, remove end of line and '>' at the beginning)
        my $cmd = "pigz -d -c -k -p $nb_threads $file | grep '>' | cut -d ' ' -f 1 | tr -d '>'";
        my @headers = `$cmd`;

        # write outputs
        my $accnr_list_f = $out_dir_assemblyaccnr_lists.$assemblyaccnr.'.txt';
        open(my $alf, '>', $accnr_list_f)or die("$prog_tag [Error] Cannot create $accnr_list_f file:$!, line ".__LINE__."\n");
        foreach(@headers)
        { 
            chomp();
            # print("prog_tag treat header $_, line ".__LINE__."\n");
            # write seq accnr list for each assembly accnr file
            print $alf "$_\n";
            # write seqaccnr taxid
	    if(not exists $h_assemblyaccnr_taxid{$assemblyaccnr})
	    {
		die "$prog_tag [Error] h_assemblyaccnr_taxid of $assemblyaccnr not found $h_assemblyaccnr_taxid{$assemblyaccnr}, line ".__LINE__."\n";
	    }
            print $st4b "$_ $h_assemblyaccnr_taxid{$assemblyaccnr}\n";
        }
        close($alf);
        print("$prog_tag $accnr_list_f file created\n");
    }
    close($st4b);    
    print("$prog_tag $out_seqaccnr_taxid_4makeblastdb_f file created\n");   
}

if($b_test_taxid_assemblyaccnr_2_seqaccnr_taxid)
{
    my $test_dir                     = "../python_scripts/";
    my $taxid_lists_dir              = '../taxid_lists/';
    my $taxid_assemblyaccnr_f        = $taxid_lists_dir.'host_complete_genomes_taxid_accnr.tsv';
    my $host_complete_genomes_db_dir = '/media/dd_travail/db/host_complete_genomes/';
    my @fna_gz_list                  = glob($host_complete_genomes_db_dir."GCF_*.fna.gz");
    my $out_seqaccnr_taxid_4makeblastdb_f = $taxid_lists_dir.'host_complete_genomes_accnr_taxid_4makeblastdb.tsv';
    my $out_dir_assemblyaccnr_lists  = $test_dir.'assemblyaccnr_seqaccnr/';
    -e $out_dir_assemblyaccnr_lists or mkdir($out_dir_assemblyaccnr_lists);
    my $nb_threads                   = 8;

    print("$prog_tag [TEST][taxid_assemblyaccnr_2_seqaccnr_taxid] START\n");
    taxid_assemblyaccnr_2_seqaccnr_taxid(
        $taxid_assemblyaccnr_f,            # tsv file woth taxid and assembly_accnr for each line
        \@fna_gz_list,                    # list of fna.gz file of the host_complete_genomes_db
        $out_seqaccnr_taxid_4makeblastdb_f, # out file dedicated to makeblastdb so as to create taxonomic link with accnr
        $out_dir_assemblyaccnr_lists,      # directory where are stored files GCF_dddddddd.d.txt list with seq accession numbers into
        $nb_threads);
    print("$prog_tag [TEST][taxid_assemblyaccnr_2_seqaccnr_taxid] END\n");
    exit();
}

return 1;
