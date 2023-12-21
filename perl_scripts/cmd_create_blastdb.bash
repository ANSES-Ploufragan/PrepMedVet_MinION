my $b_create_seqid_taxid_f = 1;
my $b_create_blastdb       = 1;

chdir($taxid_dir);

if($b_create_seqid_taxid_f)
  {
      

my @taxids_genomes_metadata = globs("*.taxids.genomes_metadata.tsv");

my $seqid_taxid_f = 'seqid_taxid.txt';
# seqid_taxid.txt Format:<SequenceId> <TaxonomyId><newline>
# used by makeblastdb to have the link between GenBank_id and taxid

open(ST,'>',$seqid_taxid_f) or die("$prog_tag [Error] Cannot create $seqid_taxid_f:$!, line ".__LINE__."\n");
for my $metadata_f(@taxids_genomes_metadata)
{
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
           print ST "$1 $taxid\n";  
         };
     }
      close(OMDF);
}
close(ST);
print("$prog_tag $seqid_taxid_f file created\n");
  }

  if($b_create_blastdb)
    {

        # create merged fasta file as stream, give it to makeblastdb
        my $cmd = "pigz -d -p 8 -k -c fasta_dir/*.fna.gz | makeblastdb -dbtype 'nucl' -input_type 'fasta' -title rvcg_blast_db -parse_seqids -out rvcg_blast_db/rvcg_blast_db -blastdb_version '5' -logfile makeblastdb_rcvg_log.txt -taxid_map $seqid_taxid_f";
        # run command and display output
        print(`$cmd`);
}
