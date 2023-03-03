#!/usr/bin/env perl
use strict;
use warnings;

my $dbdir='/db/'
my $ntdb="${db_dir}nt_blast"
my $nrdb="${db_dir}nr_blast"

my $cmd = "eval \"\$(conda shell.bash hook)\"
conda activate blast-v2.12.0
sudo mkdir $ntdb
sudo chown pmv:galaxy $ntdb
cd $ntdb
update_blastdb.pl --passive --decompress --num_threads 4 nt

sudo mkdir $nrdb
sudo chown pmv:galaxy $nrdb
cd $nrdb
update_blastdb.pl --passive --decompress --num_threads 4 nr

sudo chown -R galaxy:galaxy $ntdb
sudo chown -R galaxy:galaxy $nrdb

conda deactivate";  

print($cmd);
$b_run and print(`$cmd`);
if($@)
  {
      die("$prog_tag [Error] update_blastdb.pl failed, line ".__LINE__.":".$@."\n");
  }
  
  # then need to add path "${ntdb}" to blast tool in Galaxy
  # then need to add path "${nrdb}" to blast tool in Galaxy
