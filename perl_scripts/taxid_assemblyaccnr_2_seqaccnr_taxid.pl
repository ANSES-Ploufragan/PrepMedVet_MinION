#!/usr/bin/env perl
use warnings;
use strict;
use lib '.';
use taxid_assemblyaccnr_2_seqaccnr_taxid;
$|++;

($#ARGV == 2)or die("Usage: $0 <taxid_assemblyaccnr.tsv (in file obtained using accnr2accnr_taxid.py script on assemblyaccnr of host_complete_genomes_db)> <seqaccnr_taxid.tsv file (out file)> <host_complet_genome_db_fnagz_dir>\nExample:\n$0  ../taxid_lists/host_complete_genomes_taxid_accnr.tsv ../taxid_lists/host_complete_genomes_accnr_taxid_4makeblastdb.tsv /media/dd_travail/db/host_complete_genomes2/");

my $out_dir                      = "../python_scripts/";
my $taxid_lists_dir              = '../taxid_lists/';
my $taxid_assemblyaccnr_f        = $ARGV[0]; # $taxid_lists_dir.'host_complete_genomes_taxid_accnr.tsv';
my $host_complete_genomes_db_dir = $ARGV[2]; # '/media/dd_travail/db/host_complete_genomes2/';
my @fna_gz_list                  = glob($host_complete_genomes_db_dir."GCF_*.fna.gz");
my $out_seqaccnr_taxid_4makeblastdb_f = $ARGV[1]; # $taxid_lists_dir.'host_complete_genomes_accnr_taxid_4makeblastdb.tsv';
my $out_dir_assemblyaccnr_lists  = $out_dir.'assemblyaccnr_seqaccnr/';
-e $out_dir_assemblyaccnr_lists or mkdir($out_dir_assemblyaccnr_lists);
my $nb_threads                   = 8;

taxid_assemblyaccnr_2_seqaccnr_taxid(
    $taxid_assemblyaccnr_f,             # tsv file woth taxid and assembly_accnr for each line
    \@fna_gz_list,                      # list of fna.gz file of the host_complete_genomes_db
    $out_seqaccnr_taxid_4makeblastdb_f, # out file dedicated to makeblastdb so as to create taxonomic link with accnr
    $out_dir_assemblyaccnr_lists,       # directory where are stored files GCF_dddddddd.d.txt list with seq accession numbers into
    $nb_threads
    );
