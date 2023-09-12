#!/usr/bin/env perl
use strict;
use warnings;
use Getopt::Long;
use Cwd; # for getcwd function, provides current dir

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

get_host_completegenomes.pl

=head1 DESCRIPTION

Downloads fasta files using ncbi-genome-download for potential host complete genomes
  (needs ncbi-genome-download-0.3.1 conda env),
  Put them in a fasta_dir in the output directory (if needed, creates it)

Creates a blast db from downloaded files using makeblastdb

=head1 USAGE

=over

=item [-o <s>]

Output directory.

=item [-no_download]

If leave taxids already downloaded, avoid to download them again.

=item [-no_create_blastdb]

To deactivate blastdb creation (merging of fasta files and indexation as ncbi db)

=item [-no_accnr_list_f]

To deactivate the creation of a file listing accessionnumber.version for each seq of the db 

=item [-verbose]

To display each step done, mainly for debug.

=item [-d]

dry run: to display commands launched, does not run these commands.

=item [-t]

Only to run a test on a subset.

=back

examples:

./get_host_completegenomes.pl -h host_taxids.txt -o output_dir/

=cut

    
# **********************************************************************
my $b_verbose = 0;
my $prog_tag  = '[get_host_completegenomes.pl]';
my $b_force   = 0;
my $b_test    = 0;
my $b_run     = 1;

# **********************************************************************
# variables
# **********************************************************************
my $host_types   = 'vertebrate_mammalian,plant,invertebrate';
my $out_d                    = '';
my $host_taxid_list_f        = '';
my $host_taxid_list_leaves_f = '';
my $host_genomes_metadata_f  = '';
my $taxid_dir                = '';
my $fasta_dir                = '';
my $host_cg_accnr_f          = ''; # file that will store accession numbers of the host complete genomes of the db

my $db_name = 'host_complete_genomes_db';
my $log_f   = "host_complete_genomes_log.txt";

my $b_download               = 1;
# my $b_create_seqid_taxid_f   = 1;
my $b_create_blastdb         = 1;
my $b_create_accnr_list_of_db_for_TAXIDGENUSEXPAND = 1;

my $cmd = undef; # store commands to run

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
    "o=s"                       => \$out_d,
    "force"                     => sub { $b_force                = 1 },
    "verbose"                   => sub { $b_verbose              = 1 },
    "no_download"               => sub { $b_download             = 0 },
#    "no_seqid_taxid_f"          => sub { $b_create_seqid_taxid_f = 0 },
    "no_create_blastdb"         => sub { $b_create_blastdb       = 0 },
    "no_accnr_list_f"           => sub { $b_create_accnr_list_of_db_for_TAXIDGENUSEXPAND = 0 },
    "d"                         => sub { $b_run                  = 0 },
    "t"                         => sub { $b_test                 = 0 }
    );
my $ori_pwd = getcwd();

# **********************************************************************
# verif / deduce input output
# **********************************************************************
if($b_test)
{
    my $test_dir = './test_get_host_complete_genomes_db/';
    $out_d = $test_dir.'host_complete_genomes_db/';
    $host_genomes_metadata_f  = $out_d.$db_name.'/genomes_metadata.tsv';

    $cmd = join(' ', $0,
 		   '-o', $out_d,
 		   '-force');
     print("$prog_tag [TEST] start, we would run:\n");
     print "$cmd\n";
     print("$prog_tag [TEST] end\n");
     exit;
}

if(defined $out_d)
{
    if($out_d !~ /\/$/){ $out_d .= '/' }
}
$host_genomes_metadata_f  = $out_d.$db_name.'/genomes_metadata.tsv';

print("$prog_tag parameters:\n");
print(join("\n",
           "out_d:$out_d",
           "b_force:$b_force",
           "b_verbose:$b_verbose",
           "b_download:$b_download",
#           "b_create_seqid_taxid_f:$b_create_seqid_taxid_f",
           "b_create_blastdb:$b_create_blastdb",
           "b_run:$b_run",
           "b_test:$b_test\n"));


if($b_download)
{
    print("$prog_tag download host refseq (complete genomes chromosomes)\n"); 

    $cmd = "eval \"\$(conda shell.bash hook)\"
conda activate ncbi-genome-download-0.3.1
ncbi-genome-download -s refseq --format fasta --assembly-levels complete,chromosome -m $host_genomes_metadata_f --flat-output --output-folder ${out_d}$db_name $host_types
conda deactivate";        

    print($cmd);
    $b_run and print(`$cmd`);
    if($@)
    {
        die("$prog_tag [Error] ncbi-genome-download failed (cmd:$cmd), line ".__LINE__."\n");
    }
    print("$prog_tag $host_genomes_metadata_f file created\n");
    print("$prog_tag done\n");

}

if($b_create_blastdb)
{
    print("$prog_tag move to $out_d dir\n");
    chdir($out_d);
    my $pwd_str = getcwd();
    -e $out_d.$db_name or mkdir($out_d.$db_name);

    print("$prog_tag uncompress fasta files, create blastdb in ${pwd_str}$db_name directory\n");
    # create merged fasta file as stream, give it to makeblastdb
    my $cmd = "pigz -d -p 8 -k -c ${out_d}*.fna.gz | makeblastdb -dbtype 'nucl' -input_type 'fasta' -title $db_name -parse_seqids -out ${out_d}$db_name -blastdb_version '5' -logfile ${out_d}$log_f ";
    # -taxid_map ${out_d}$seqid_taxid_f"; # allow to have informations: accnr taxid for each seq
    # run command and display output
    print("$prog_tag $cmd\n");
    my @res = ();
    if($b_run)
    {
        @res = `$cmd`;
        print(@res);
        print("$prog_tag done\n");
        if($@)
        {
            exit("$prog_tag [Error]:$@\n");
        }
        print("prog_tag $log_f log file of makeblastdb created\n");
    }
}

if($b_create_accnr_list_of_db_for_TAXIDGENUSEXPAND)
{
    # get accession numbers with version for fasta files of the db
    my $cmd = "ls *.fna.gz | cut -d '.' -f 1,2 > $host_cg_accnr_f";

    print("$prog_tag $cmd\n");
    my @res = ();
    if($b_run)
    {
        @res = `$cmd`;
        print(@res);
        print("$prog_tag $host_cg_accnr_f file created line ".__LINE__."\n");
        if($@)
        {
            exit("$prog_tag [Error]:$@\n");
        }
    }
}

print("$prog_tag move to $ori_pwd dir\n");
chdir($ori_pwd);




