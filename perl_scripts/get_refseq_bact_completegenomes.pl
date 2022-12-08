#!/usr/bin/env perl
use strict;
use warnings;
use Getopt::Long;


# **********************************************************************
# For windows portability?
# see http://perldoc.perl.org/perlport.html for portability
# **********************************************************************
BEGIN {
    if ($^O =~ /^(MS)?Win/) {
        eval "use Win32::DriveInfo";
    }
}
# **********************************************************************

=head1  NAME

get_refseq_virus_completegenomes.pl

=head1 DESCRIPTION

From the README file of PrepMedVet_analyses/taxid_lists/:
- deduce viral pathogen taxids (viral but from order, genious, or whatever):
- deduce, foreach, a list of species taxids (leave taxids), by using get_species_taxids.sh
  included in blast+ (needs blast-v2.12.0 conda env)
  Put them in a taxid_dir in the output directory (if needed, creates it)
- get metadata
- download fasta files using ncbi-genome-download (needs ncbi-genome-download-0.3.1 conda env)
  Put them in a fasta_dir in the output directory (if needed, creates it)

Then remove taxid files.

=head1 USAGE

=over

=item -r <s>

README.md file of PrepMedVet_analyses/taxid_lists
(describe taxids used in pathogens and hosts with their scientific name, taxids follow '(taxid: ' string)
Viral taxid are obtained by case insensitive grep with 'virid|viral|viria|virus|phage' terms.

=item [-o <s>]

Output directory.

=item [-no_download_taxid]

If leave taxids already downloaded, avoid to download them again.

=item [-keep_taxid]

To keep files listing leave taxids. By default, remove them.

=item [-verbose]

To display each step done, mainly for debug.

=item [-t]

Only to run a test on a subset.

=back

examples:

./get_refseq_virus_completegenomes.pl -r README.md -o output_dir/

=cut

    
# **********************************************************************
my $b_verbose = 0;
my $prog_tag  = '[get_refseq_virus_completegenomes.pl]';
my $b_force   = 0;
my $b_test    = 0;

# **********************************************************************
# variables
# **********************************************************************
my $taxid_README_f = '/home/touzain/Documents/PrepMedVet_analyses/taxid_lists/README.md';
my $out_d                           = '';
my $patho_viral_taxid_list_f        = '';
my $patho_viral_taxid_list_leaves_f = '';
my $patho_viral_genomes_metadata_f  = '';
my $taxid_dir                       = '';
my $fasta_dir                       = '';

my $b_no_download_taxid = 0;
my $b_remove_taxid_f    = 0;

# **********************************************************************
# CHECK OPTIONS
# **********************************************************************
my $nbargmini = 1;

if(scalar(@ARGV) < $nbargmini){ 
  print "Bad number of arguments: ".scalar(@ARGV)." found, at least $nbargmini wanted\n";
  foreach(0..$#ARGV){
    print "$_: $ARGV[$_]\n";
  }
  die `perldoc $0`;
}
GetOptions( 
    "r=s"               => \$taxid_README_f,
    "o=s"               => \$out_d,
    "force"             => sub { $b_force             = 0 },
    "verbose"           => sub { $b_verbose           = 0 },    
    "no_download_taxid" => sub { $b_no_download_taxid = 0 },
    "keep_taxid"        => sub { $b_remove_taxid_f    = 0 },
    "t"                 => sub { $b_test              = 0 }    
    );
# **********************************************************************
# verif / deduce input output
# **********************************************************************
if($b_test)
{
    $taxid_README_f = '../taxid_lists/README.md';
    my $test_dir = './test_get_refseq_virus_completegenomes/';
    $out_d = $test_dir.'refseq_virus_completegenomes_test/';
    $patho_viral_taxid_list_f        = $out_d.'patho_viral_taxid_list.txt';
    $patho_viral_taxid_list_leaves_f = $out_d.'patho_viral_taxid_list_leaves.txt';
    $patho_viral_genomes_metadata_f  = $out_d.'genomes_metadata.tsv';
    $taxid_dir                       = $out_d.'taxid_dir/';
    $fasta_dir                       = $out_d.'fasta_dir/';

    my $cmd = join(' ', $0,
 		   '-r', $taxid_README_f,
 		   '-o', $out_d,
 		   '-force');
     print("$prog_tag [TEST] start, we would run:\n");
     print "$cmd\n";
     print("$prog_tag [TEST] end\n");
     exit;
}
else
{
    $patho_viral_taxid_list_f        = $out_d.'patho_viral_taxid_list.txt';
    $patho_viral_taxid_list_leaves_f = $out_d.'patho_viral_taxid_list_leaves.txt';
    $patho_viral_genomes_metadata_f  = $out_d.'genomes_metadata.tsv';
    $taxid_dir                       = $out_d.'taxid_dir/';
    $fasta_dir                       = $out_d.'fasta_dir/';
     
}
-e $taxid_dir or mkdir $taxid_dir;
-e $fasta_dir or mkdir $fasta_dir;

print("$prog_tag creates $patho_viral_taxid_list_f file with global viral taxids of pathogens\n");
my $cmd = "grep -E -i -v 'virid|viral|viria|virus|phage' $taxid_README_f | grep -E -v '^\#' | perl -p -e \"s/^.*\\(taxid: \(\\d+\)\\).*\$/\\1/\" > $patho_viral_taxid_list_f";
print("$prog_tag cmd:$cmd\n");
`$cmd`;
print("$prog_tag done, $patho_viral_taxid_list_f file created\n");

# get species taxids (leaves instead of general genus/order taxids)
open(TAXID,'<',$patho_viral_taxid_list_f)or die("$prog_tag [Error] Cannot open $patho_viral_taxid_list_f file, line ".__LINE__."\n");

print("$prog_tag deduce leaves taxids for each taxid found in $patho_viral_taxid_list_f\n");
my @taxid_files = ();
while(my $line=<TAXID>)
{
    chomp($line);
    my $taxid_file = $taxid_dir."$line.taxids";
    print("$prog_tag \tget leave taxids from $line\n");
    if(not $b_no_download_taxid)
    {
        $cmd = `eval \"\$(conda shell.bash hook)\"
conda activate blast-v2.12.0
get_species_taxids.sh -t $line > $taxid_file
conda deactivate`;
    }
    push @taxid_files, "$taxid_file";
}
print("$prog_tag done\n");
close(TAXID);

print("$prog_tag record all viral leaves taxids in $patho_viral_taxid_list_leaves_f\n");
$cmd = join(' ', 'cat', @taxid_files, " > $patho_viral_taxid_list_leaves_f");
`$cmd`;
print("$prog_tag created\n");

print("$prog_tag download viral refseq of leave taxid:\n"); 
foreach my $taxid_f(@taxid_files)
{
    my $taxid_metadata_f = $taxid_f.'.genomes_metadata.tsv';
    $cmd = `eval \"\$(conda shell.bash hook)\"
conda activate ncbi-genome-download-0.3.1
ncbi-genome-download -s refseq --format fasta --assembly-levels complete --taxids $taxid_f -m $taxid_metadata_f --flat-output viral --output-folder $fasta_dir --flat-output
conda deactivate`;
    print($cmd);

    if($@)
    {
	die("$prog_tag [Error] ncbi-genome-download failed for $taxid_f, line ".__LINE__."\n");
    }
    else
    {
	print("$prog_tag \tget metadata for $taxid_f file\n");
	`cat $taxid_metadata_f >> $patho_viral_genomes_metadata_f`;
	print("$prog_tag \tdone\n");
	if($b_remove_taxid_f)
	{
	    unlink $taxid_f;
	    print("$prog_tag \t$taxid_f deleted\n");
	}
    }
}
print("$prog_tag $patho_viral_genomes_metadata_f file created\n");
print("$prog_tag done\n");

# print("$prog_tag cleaning individual leave taxid files\n");
# unlink @taxid_files;
# print("$prog_tag done\n");




# # perl -p -e 's/\n/,/' | perl -p -e 's/,$//' >


# # to download refseq virus COMPLETE SEQUENCES only using viral pathogen taxids
# # WARNING: maybe taxid must be leaves for ncbi, check perl script provided by ncbi to get leaves when providing any taxid
# # -n for dry-run
# conda activate ncbi-genome-download-0.3.1
# ncbi-genome-download --section refseq --format fasta --assembly-levels complete --taxids patho_viral_taxid_list.txt -m genomes_metadata.tsv --flat-output viral -n


# # phages mainly, but ok
# ncbi-genome-download --section refseq --format fasta -assembly-levels complete --taxids 10292.taxids -n viral

