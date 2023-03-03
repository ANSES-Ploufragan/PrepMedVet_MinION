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
- then remove taxid files.

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

=item [-no_seqid_taxid_f]

To deactivate parsing of taxid.metadata.tsv files created by ncbi-genome-download.
Deativate when blastdb is already created.

=item [-no_create_blastdb]

To deactivate blastdb creation (merging of fasta files and indexation as ncbi db)

=item [-verbose]

To display each step done, mainly for debug.

=item [-d]

dry run: to display commands launched, does not run these commands.

=item [-t]

Only to run a test on a subset.

=item [-b]

Bacterial/ to treat bacteria/archae/fungi db instead of virus/phages db.
(default viral/phagic)

=back

examples:

./get_refseq_virus_completegenomes.pl -r README.md -o output_dir/

=cut

    
# **********************************************************************
my $b_verbose = 0;
my $prog_tag  = '[get_refseq_virus_completegenomes.pl]';
my $b_force   = 0;
my $b_test    = 0;
my $b_run     = 1;

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

my $db_name = 'rvcg_blast_db';
my $log_f   = "makeblastdb_rvcg_log.txt";

my $b_get_patho_taxid_leaves = 1;
my $b_download_taxid         = 1;
my $b_remove_taxid_f         = 1;
my $b_create_seqid_taxid_f   = 1;
my $b_create_blastdb         = 1;
my $b_viral                  = 1;

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
    "r=s"                       => \$taxid_README_f,
    "o=s"                       => \$out_d,
    "force"                     => sub { $b_force                = 1 },
    "verbose"                   => sub { $b_verbose              = 1 },
    "no_get_patho_taxid_leaves" => sub { $b_get_patho_taxid_leaves = 0 },
    "no_download_taxid"         => sub { $b_download_taxid       = 0 },
    "keep_taxid"                => sub { $b_remove_taxid_f       = 0 },
    "no_seqid_taxid_f"          => sub { $b_create_seqid_taxid_f = 0 },
    "no_create_blastdb"         => sub { $b_create_blastdb       = 0 },
    "d"                         => sub { $b_run                  = 0 },
    "t"                         => sub { $b_test                 = 0 },
    "b"                         => sub { $b_viral                = 0 }
    );
my $ori_pwd = getcwd();

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

    $cmd = join(' ', $0,
 		   '-r', $taxid_README_f,
 		   '-o', $out_d,
 		   '-force');
     print("$prog_tag [TEST] start, we would run:\n");
     print "$cmd\n";
     print("$prog_tag [TEST] end\n");
     exit;
}
elsif($b_viral)
{
    $patho_viral_taxid_list_f        = $out_d.'patho_viral_taxid_list.txt';
    $patho_viral_taxid_list_leaves_f = $out_d.'patho_viral_taxid_list_leaves.txt';
}
else
{
    $patho_viral_taxid_list_f        = $out_d.'patho_bact_taxid_list.txt';
    $patho_viral_taxid_list_leaves_f = $out_d.'patho_bact_taxid_list_leaves.txt';
}
$patho_viral_genomes_metadata_f  = $out_d.'genomes_metadata.tsv';
$taxid_dir                       = $out_d.'taxid_dir/';
$fasta_dir                       = $out_d.'fasta_dir/';    

print("$prog_tag parameters:\n");
print(join("\n",
           "taxid_README_f:$taxid_README_f",
           "out_d:$out_d",
           "b_force:$b_force",
           "b_verbose:$b_verbose",
           "b_download_taxid:$b_download_taxid",
           "b_remove_taxid:$b_remove_taxid_f",
           "b_create_seqid_taxid_f:$b_create_seqid_taxid_f",
           "b_create_blastdb:$b_create_blastdb",
           "b_run:$b_run",
           "b_test:$b_test",
           "b_viral:$b_viral\n"));

if(not $b_viral)
{
    $db_name = 'rbcg_blast_db';
    $log_f   = "makeblastdb_rbcg_log.txt"; 
}


-e $taxid_dir or mkdir $taxid_dir;
-e $fasta_dir or mkdir $fasta_dir;

my @taxid_files = ();
if($b_get_patho_taxid_leaves)
{
    print("$prog_tag creates $patho_viral_taxid_list_f file with global viral taxids of pathogens\n");

    if($b_viral)
    {
        $cmd = "grep 'taxid:' $taxid_README_f | grep -E -i 'virid|viral|viria|virus|phage' | grep -E -v '^\#' | perl -p -e \"s/^.*\\(taxid: \(\\d+\).*\$/\\1/\" > $patho_viral_taxid_list_f";            
    }
    else
    {
        $cmd = "grep 'taxid:' $taxid_README_f | grep -E -i -v 'virid|viral|viria|virus|phage' | grep -E -v 'vertebrates|dipter|nematod|vegetables|tiques|puces' | grep -E -v '^\#' | perl -p -e \"s/^.*\\(taxid: \(\\d+\).*\$/\\1/\" > $patho_viral_taxid_list_f";
    }

    print("$prog_tag cmd:$cmd\n");
    $b_run and `$cmd`;
    print("$prog_tag done, $patho_viral_taxid_list_f file created\n");

    if($b_run)
    {
        # get species taxids (leaves instead of general genus/order taxids)
        open(TAXID,'<',$patho_viral_taxid_list_f)or die("$prog_tag [Error] Cannot open $patho_viral_taxid_list_f file, line ".__LINE__."\n");
        
        print("$prog_tag deduce leaves taxids for each taxid found in $patho_viral_taxid_list_f\n");
        
        while(my $line=<TAXID>)
        {
            chomp($line);
            my $taxid_file = $taxid_dir."$line.taxids";
            
            if($b_download_taxid)
            {
                print("$prog_tag \tget leave taxids from $line\n");
                $cmd = "eval \"\$(conda shell.bash hook)\"
conda activate blast-v2.12.0
get_species_taxids.sh -t $line > $taxid_file
conda deactivate";
                print(`$cmd`);
            }
            push @taxid_files, "$taxid_file";
        }
        print("$prog_tag done\n");
        close(TAXID);
    }

    print("$prog_tag record all viral leaves taxids in $patho_viral_taxid_list_leaves_f\n");
    $cmd = join(' ', 'cat', @taxid_files, " > $patho_viral_taxid_list_leaves_f");
    $b_run and `$cmd`;
    print("$prog_tag created\n");
}

if($b_download_taxid)
{
    print("$prog_tag download viral refseq of leave taxid:\n"); 
    foreach my $taxid_f(@taxid_files)
    {
        my $taxid_metadata_f = $taxid_f.'.genomes_metadata.tsv';

        if($b_viral)
        {
            $cmd = "eval \"\$(conda shell.bash hook)\"
conda activate ncbi-genome-download-0.3.1
ncbi-genome-download -s refseq --format fasta --assembly-levels complete --taxids $taxid_f -m $taxid_metadata_f --flat-output viral --output-folder $fasta_dir --flat-output
conda deactivate";        
        }
        else
        {
            $cmd = `eval \"\$(conda shell.bash hook)\"
conda activate ncbi-genome-download-0.3.1
ncbi-genome-download -s refseq --format fasta --assembly-levels complete --taxids $taxid_f -m $taxid_metadata_f --flat-output --output-folder $fasta_dir --flat-output bacteria,fungi,archaea,invertebrate
conda deactivate`;

        }
        print($cmd);
        $b_run and print(`$cmd`);
        if($@)
        {
            die("$prog_tag [Error] ncbi-genome-download failed for $taxid_f, line ".__LINE__."\n");
        }
        else
        {
            print("$prog_tag \tget metadata for $taxid_f file\n");
            $cmd = "cat $taxid_metadata_f >> $patho_viral_genomes_metadata_f";
            $b_run and print(`$cmd`);
            print("$prog_tag \tdone\n");
            if($b_remove_taxid_f)
            {
                $b_run and unlink $taxid_f;
                print("$prog_tag \t$taxid_f deleted\n");
            }
        }
    }
    print("$prog_tag $patho_viral_genomes_metadata_f file created\n");
    print("$prog_tag done\n");

    # print("$prog_tag cleaning individual leave taxid files\n");
    # unlink @taxid_files;
    # print("$prog_tag done\n");
}

# go to db taxid_dir
print("$prog_tag move to $taxid_dir dir\n");
chdir($taxid_dir);

# creates seqid_taxid file with GenBlank IDs and taxids to be used by blastdbcmd (allow to know
# taxonomy when doing a blast)
my $seqid_taxid_f = 'seqid_taxid.txt';
if($b_create_seqid_taxid_f)
{
    print("$prog_tag get all taxids.genomes_metadata.tsv files\n");
    my @taxids_genomes_metadata = glob("*.taxids.genomes_metadata.tsv");

    print("$prog_tag deduce $seqid_taxid_f files\n");
    # seqid_taxid.txt Format:<SequenceId> <TaxonomyId><newline>
    # used by makeblastdb to have the link between GenBank_id and taxid
    
    $b_run and (open(ST,'>',$seqid_taxid_f) or die("$prog_tag [Error] Cannot create $seqid_taxid_f:$!, line ".__LINE__."\n"));
    for my $metadata_f(@taxids_genomes_metadata)
    {
        my $taxid = '';
        if($metadata_f =~ /^(\d+)/)
        {
            # get taxid
            $taxid = $1;
        }
        open(OMDF,'<',$metadata_f)or die("$prog_tag [Error] Cannot open $metadata_f:$!, line ".__LINE__."\n");
        while(<OMDF>)
        {
            # get fasta GenBank identifier
            /^>(\S+)/ and do
            {
                # print in file genbankid taxid
                if($b_run){ print ST "$1 $taxid\n";  }
                else      { print    "$1 $taxid\n";  }
            };
        }
        $b_run and close(OMDF);
    }
    $b_run and close(ST);
    print("$prog_tag $seqid_taxid_f file created\n");
}

if($b_create_blastdb)
{
    print("$prog_tag move to .. dir\n");
    chdir('..');
    my $pwd_str = getcwd();
    -e $db_name or mkdir($db_name);

    print("$prog_tag uncompress fasta files, create blastdb in ${pwd_str}$db_name directory\n");
    # create merged fasta file as stream, give it to makeblastdb
    my $cmd = "pigz -d -p 8 -k -c fasta_dir/*.fna.gz | makeblastdb -dbtype 'nucl' -input_type 'fasta' -title $db_name -parse_seqids -out $db_name/$db_name -blastdb_version '5' -logfile $log_f -taxid_map ${taxid_dir}$seqid_taxid_f";
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
print("$prog_tag move to $ori_pwd dir\n");
chdir($ori_pwd);


