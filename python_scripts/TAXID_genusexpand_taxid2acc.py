#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###
# USE PYTHON3
# From a file of taxid and accession numbers (tsv), deduce species taxids, get ref genome acc nr list (all chr). (it will allow to have complete genomes when aligning with host to remove host reads)
# provide 2 files:
# - file with all acc numbers that are included in taxid(s) provided by user (extended to genus level)
# - file with all acc numbers that are excluded in taxid(s) provided by user (extended to genus level)
###

### Libraries to import:
import argparse, os, sys, csv, warnings, re, itertools, operator
#from subprocess import Popen,PIPE
import subprocess
from os import path
import ncbi_genome_download as ngd
# to find all lineage and in case of no complete genome, the deduction of closests complete genomes (same genus, order...)
from ete3 import NCBITaxa

# to be able to report line number in error messages
import inspect
frame = inspect.currentframe()

# debug
test_dir = 'test_TAXID_genusexpand_taxid2acc/'
b_test_load_taxids = False                             # ok 2023 08 25
b_test_add_host_chr_taxids_accnr_from_ori_list = False # ok 2023 08 25

prog_tag = '[' + os.path.basename(__file__) + ']'

# boolean to know if we dowload ncbi taxonomy file in current env
b_load_ncbi_tax_f = False

# list of interesting taxid (fathers)
taxidlist_f = ''
taxidlist = []
accnrlist = []
    
# order = -4
# family or clade = -3
# subtribe or genus = -2
curr_index_in_lineage = -2
min_index_in_lineage = -4

# boolean to know if we download ncbi taxonomy file in current env
b_load_ncbi_tax_f = False
b_test_all        = False
b_test            = False
b_acc_in_f        = False
b_acc_out_f       = False

b_verbose         = False

# variables for ncbi-genome-download
ncbigenomedownload_section = 'refseq' # genbank
organisms_to_search_in = 'vertebrate_other,vertebrate_mammalian,plant,invertebrate'
assembly_levels = 'complete,chromosome'

# rank = '' # rank level retained by user
# rank_num = index of rank retained by user

# # set to check that provided rank exist to be sure to be able to use it
# ranks = {
#     'superkingdom' => 0,
#     # 'clade', # no, several clade, name is too generic
#     'kingdom'      => 1,
#     'phylum'       => 2,
#     'subphylum'    => 3,
#     'superclass'   => 4,
#     'class'        => 5,
#     'superorder'   => 6,
#     'order'        => 7,
#     'suborder'     => 8,
#     'infraorder'   => 9,
#     'parvorder'    => 10,
#     'superfamily'  => 11,
#     'family'       => 12,
#     'subfamily'    => 13,
#     'genus'        => 14,
#     'species'      => 15,
#     'subspecies'   => 16
#     }

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--taxid_acc_in_f", dest='taxid_acc_in_f',
                    help="taxid acc_number list in tsv (tabular separated at each line)",
                    metavar="FILE")
parser.add_argument("-o", "--acc_out_f", dest='acc_out_f',
                    help="[optional if --taxid_acc_in_f provided] Output text file with accession numbers of COMPLETE GENOMES under taxid in ncbi taxonomy tree",
                    metavar="FILE")
# parser.add_argument("-r", "--rank", dest='rank',
#                     help="[Optional] default: genus, rank to retain for each acc number provided. We will retain all the acc number descendant from this 'rank' (genus) taxid list",
#                     action="store_const")
parser.add_argument("-n", "--ncbi_tax_f", dest='ncbi_tax_f',
                    help="[Optional] ncbi tabular file with taxonomy organized to represent a tree",
                    metavar="FILE")
parser.add_argument("-l", "--load_ncbi_tax_f", dest='b_load_ncbi_tax_f',
                    help="[Optional] load ncbi tabular file with taxonomy organized to represent a tree in current env at default location (~/.etetoolkit/taxa.sqlite). Only needed for first run",
                    action='store_true')
parser.add_argument("-z", "--test_all", dest='b_test_all',
                    help="[Optional] run all tests. Additionally, with --load_ncbi_tax_f, allow to download ncbi ete3 tax db the first time you use the script",
                    action='store_true')
parser.add_argument("-v", "--verbose", dest='b_verbose',
                    help="[Optional] To have details on records when running",
                    action='store_true')
parser.set_defaults(b_load_ncbi_tax_f=False)
parser.set_defaults(b_test_all=False)
parser.set_defaults(b_verbose=False)

# get absolute path in case of files
args = parser.parse_args()

# -------------------------------------------
# check arguments
b_test_all = args.b_test_all

if b_test_all:
    b_test_load_taxids = False
    b_test_add_host_chr_taxids_accnr_from_ori_list = True 
    b_test = True
    b_acc_in_f = True
    b_acc_out_f = True
else:
    b_test = (b_test_load_taxids or
              b_test_add_host_chr_taxids_accnr_from_ori_list)

if ((not b_test)and
    ((len(sys.argv) < 2) or (len(sys.argv) > 5))):
    print("\n".join([
        "Aim: find accession numbers of complete genomes related to provided taxids.",
        "If not found at species level, try at upper taxonomic level until order.",
        "Retains only 1 complete genome is several available:",
        "  - the one with the highest version number, if not sufficient",
        "  - the one with the highest accession number",        
        "To use this scripts, run:",
        "conda activate TAXID_genusexpand_taxid2acc",
        "./TAXID_genusexpand_taxid2acc.py --test_all --load_ncbi_tax_f",
        " ",
        "Then you won't need --test_all --load_ncbi_tax_f options\n\n",
        "Then, as an example:\n\n",
        ' '.join(['./TAXID_genusexpand_taxid2acc.py',
                  '-i taxid_accnr_list.tsv',
                  '-o accnr_out_list.txt']),"\n\n" ]))
    parser.print_help()
    print(prog_tag + "[Error] we found "+str(len(sys.argv)) +
          " arguments, exit line "+str(frame.f_lineno))
    sys.exit(0)

# print('args:', args)
# if(not b_test):
if args.ncbi_tax_f is not None:
    ncbi_tax_f = os.path.abspath(args.ncbi_tax_f)
else:
    # ncbi_tax_f = "/nfs/data/db/ete3/taxa.sqlite"
    ncbi_tax_f = os.path.expanduser("~/.etetoolkit/taxa.sqlite")
if args.taxid_acc_in_f is not None:
    taxid_acc_in_f = os.path.abspath(args.taxid_acc_f)
    b_acc_in_f = True    
elif(not b_test):
    sys.exit("[Error] You must provide taxid_acc_in_f")
if args.acc_out_f is not None:
    acc_out_f = os.path.abspath(args.acc_out_f)
    b_acc_out_f = True
elif(not b_test):
    sys.exit("-acc_out_f <accnr_file>n must be provided\n")
# if args.rank is not None:
#     rank = 'genus'
# else:
#     rank = args.rank
    
if args.b_verbose is not None:
    b_verbose = int(args.b_verbose)

if(not b_test):
    if (not b_acc_in_f) and (not b_acc_out_f):
        sys.exit(prog_tag + "[Error] You must provide either --acc_f <file> and -acc_out_f <file>")

# # store index of the rank expected by user
# rank_num = ranks{ rank }

# --------------------------------------------------------------------------
# to sort uniq, for a list, only need to add list conversion
# --------------------------------------------------------------------------
mapper= map # Python ≥ 3
def sort_uniq(sequence):
    return mapper(
        operator.itemgetter(0),
        itertools.groupby(sorted(sequence)))
# --------------------------------------------------------------------------

# --------------------------------------------------------------------------
# Procedure: load taxid acc list, return taxidlist
# --------------------------------------------------------------------------
def load_taxids(taxid_acc_tabular_f):

    if not path.exists(taxid_acc_tabular_f):
        sys.exit("Error " + taxid_acc_tabular_f +
                 " file does not exist, line "+ str(sys._getframe().f_lineno) )

    cmd = "cut -f 1,2 "+taxid_acc_tabular_f+" | sort | uniq "

    for line in os.popen(cmd).readlines():
        if line.rstrip() != "":
            k, v = line.rstrip().split()
            taxidlist.append(k)
            accnrlist.append(v)
            # print(f"last item added to accnrlist:{accnrlist[-1]}, line {str(sys._getframe().f_lineno)}")

# --------------------------------------------------------------------------

# test load_taxids function
# display taxidlist, then exit
if b_test_load_taxids:
    taxid_acc_tabular_f = test_dir + 'megablast_out_f_taxid_acc_host.tsv'
    print("START b_test_load_taxids")
    print("loading "+taxid_acc_tabular_f+" file")
    load_taxids(taxid_acc_tabular_f)
    for i in range(len(taxidlist)):
        print(f"{taxidlist[i]}\t{accnrlist[i]}")
    print("END b_test_load_taxids")
    if not b_test_add_host_chr_taxids_accnr_from_ori_list:
        sys.exit()
# --------------------------------------------------------------------------

# # --------------------------------------------------------------------------
# # needs internet connexion, not possible
# # --------------------------------------------------------------------------
# def get_leave_taxid_from_acc_nr(accnrlist):

#     # deduce a list of taxid from a list of accession numbers
#     cmd = "cat megablast_out_f_acc_out_taxid.tsv | epost -db nuccore | esummary | xtract -pattern DocumentSummary -element TaxId | sort -u"
#     for line in os.popen(cmd).readlines():
#         taxidlist.append(line.rstrip())

#     return taxidlist
# # --------------------------------------------------------------------------

# --------------------------------------------------------------------------
# function to retain the most recent acc nr for host complete genome found:
# - return acc nr of most recent complete genome
# - print accnr species and name retained
# - reinitiate tmp lists of accnrlisttmp speciestmp and nametmp 
# --------------------------------------------------------------------------
def retain_1accnr(accnrlisttmp, speciestmp, nametmp):

    max_accnr_version  = 0
    curr_accnr_version = 0
    max_accnr_nr       = 0
    curr_accnr_nr      = 0
    kept_accnr_i       = 0
    p = re.compile(".*?(\d+)\.(\d+)$")

    # print(f"{prog_tag} retain_1accnr({accnrlisttmp}, {speciestmp}, {nametmp}")

    for i in range(len(accnrlisttmp)):
        m = p.match( accnrlisttmp[i] )
        if m:
            # print('Match found: ', m.group(2))
            curr_accnr_version = int(m.group(2))
            accnr_nr = int(m.group(1))
            if curr_accnr_version > max_accnr_version:
                max_accnr_version = curr_accnr_version
                kept_accnr_i = i
                # print(f"record kept_accnr_i:{kept_accnr_i}")
            elif(( curr_accnr_version == max_accnr_version)and
                 (curr_accnr_nr > max_accnr_nr)):
                max_accnr_nr = curr_accnr_nr
                kept_accnr_i = i
                # print(f"record kept_accnr_i:{kept_accnr_i}")
            
        else:
            sys.exit(f"{prog_tag} No version found for accnr:{accnrlisttmp[i]}")
            
    print(f"retained accnr:{accnrlisttmp[kept_accnr_i]}\tspecies:{speciestmp[kept_accnr_i]}\tname:{nametmp[kept_accnr_i]}")
    kept_accn = accnrlisttmp[kept_accnr_i]

    return kept_accn
# --------------------------------------------------------------------------

# --------------------------------------------------------------------------
# Function to find complete genome closely related to current taxid
# goes upper in taxonomy if nothing found until order
# --------------------------------------------------------------------------
def ngd_upper_lineage(curr_index_in_lineage,
                      lineage,
                      ncbi,                      
                      accnrlisttmp, # current working list
                      accnrlist,    # final list, if something added (or min index reached), recursivity stop
                      speciestmp,
                      nametmp
                      ):
    print(f"{prog_tag} ngd_upper_lineage with curr_index_in_lineage:{curr_index_in_lineage}")
    
    # deduce up rank, search complet genome/chr in
    upper_taxid=str(lineage[curr_index_in_lineage]) # order when last is species
    rank = ncbi.get_rank([lineage[curr_index_in_lineage]])
    name = ncbi.get_taxid_translator([lineage[curr_index_in_lineage]])
    print(f"{prog_tag} test with taxid:{upper_taxid} corresponding to rank:{rank}")
    leaves_taxids = ncbi.get_descendant_taxa(upper_taxid,
                                             intermediate_nodes=False,
                                             collapse_subspecies=False,
                                             return_tree=False
                                             )

    # int conversion to strings
    leaves_taxids = list(map(str, leaves_taxids))
    leaves_taxids_list = ','.join(leaves_taxids)

    if b_verbose:
        print(f"{prog_tag} leaves_taxids for taxid {upper_taxid}:{leaves_taxids_list}")    
    cmd = f"ncbi-genome-download -s {ncbigenomedownload_section} --taxids {leaves_taxids_list} --assembly-levels {assembly_levels} --dry-run {organisms_to_search_in} 2>&1"
    if b_verbose:
        print(f"{prog_tag} cmd:{cmd}")

    # specific to retain_1accn to avoid lists are crashed by other ngd call
    accnrlisttmp_r = []
    speciestmp_r   = []
    nametmp_r      = []
    
    for line in os.popen(cmd).readlines():
#        print(f"line 314:{line.rstrip()}")
        if not re.match("^Considering", line):
#            print(f"line 316:{line.rstrip()}")
            if re.match("^(?:ERROR|Error): No downloads", line):
                print(f"{prog_tag} No chr/complete genome for taxid:{upper_taxid} rank:{rank} (expanding name:{name})")
                if curr_index_in_lineage > min_index_in_lineage: # need to go on with upper lineage if not last accepted
                    curr_index_in_lineage = curr_index_in_lineage - 1
                    print(f"{prog_tag} ngd_upper_lineage call {curr_index_in_lineage} line {str(sys._getframe().f_lineno)}") 
                    return ngd_upper_lineage(curr_index_in_lineage,
                                             lineage,
                                             ncbi,                                      
                                             accnrlisttmp, # current working list
                                             accnrlist,    # final list, if something added (or min index reached), recursivity stop
                                             speciestmp,
                                             nametmp                                     
                                             )
            else:
#                print(f"line 331:{line}")
                try:
                    acc_nr, species, name = line.rstrip().split("\t")
                except ValueError as ve:
                    sys.exit(f"ValueError {ve}: for split of line '{line}'")
                accnrlisttmp_r.append(acc_nr)
                speciestmp_r.append(species)
                nametmp_r.append(name)                                  
                if b_verbose:
                    print(f"{prog_tag} we found for {species} chr fasta for host genome with accnr {acc_nr} (name:{name})")

                # retain only the most recent complete genome for current treated taxid
                return retain_1accnr(accnrlisttmp_r, speciestmp_r, nametmp_r)
                
        # else:
        #     print(f"line matching Considering:{line}")
# --------------------------------------------------------------------------

# --------------------------------------------------------------------------
# read taxids, deduce complete genomes available in genblank, provides in output file
# the acc number in addition  to those already listed
# --------------------------------------------------------------------------
def add_host_chr_taxids_accnr_from_ori_list(taxidlist,
                                            accnrlist,
                                            acc_out_f):

    # store all accnr found for complete genome of current taxid (or from same family/order)
    # the aim is to keep only the most recent/complete
    accnrlisttmp = []
    speciestmp   = []
    nametmp      = []
        
    # get host complete genome when found using ncbi_genome_download
    taxids_list=','.join(taxidlist)

    # # ------------------------------------------
    # # ncbi-genome-download as a library
    # ngd_out_f= os.getcwd()+'/accnr_sp_accnr.tsv'
    # ngd.download(section=ncbigenomedownload_section,
    #              taxids=taxids_list,
    #              assembly_levels=assembly_levels,
    #              flat_output=True,
    #              output=ngd_out_f,
    #              groups=organisms_to_search_in,
    #              dry_run=True   
    #              )


    # cmd = "cut -f 1,2 "+ngd_out_f

    # for line in os.popen(cmd).readlines():
    #     acc_nr, species = line.rstrip().split()
    #     accnrlist.append(acc_nr)

    #     if b_verbose:
    #         print(f"{prog_tag} we found for {species} chr fasta for host genome with accnr {acc_nr}")
    # # ------------------------------------------

    # ------------------------------------------
    # ncbi-genome-download as executable script
    # ------------------------------------------

    # load NCBITaxa
    ncbi = NCBITaxa()   # Install ete3 db in local user file (.ete_toolkit/ directory)
    print(prog_tag + " Try to load ncbi tax db file:"+ncbi_tax_f)
    ncbi = NCBITaxa(dbfile=ncbi_tax_f)
    if (not os.path.isfile(ncbi_tax_f)) or b_load_ncbi_tax_f:
        try:
            ncbi.update_taxonomy_database()
        except:
            warnings.warn(prog_tag+"[SQLite Integrity error/warning] due to redundant IDs")

    for taxid_u in taxidlist:
        print(f"{prog_tag} treating global taxid:{taxid_u}")
        cmd = f"ncbi-genome-download -s {ncbigenomedownload_section} --taxids {taxid_u} --assembly-levels {assembly_levels} --dry-run {organisms_to_search_in} 2>&1"
        for line in os.popen(cmd).readlines():
            if b_verbose:
                print(f"{prog_tag} cmd:{cmd} ran, read output")
            # ERROR: No downloads matched your filter. Please check your options.
            if re.match("^(?:ERROR|Error): No downloads", line):
                # get complete lineage: accept ONLY leave taxid? (species)
                lineage = ncbi.get_lineage(int(taxid_u))
                name = ncbi.translate_to_names(lineage)
                if b_verbose:
                    print(f"taxid:{taxid_u}\tlineage:{lineage}\tname:{name}")

                # same search but going upper in taxonomy, finding leaves taxid to find new closeley related complete genome
                # print(f"{prog_tag} ngd_upper_lineage call {curr_index_in_lineage} line {str(sys._getframe().f_lineno)}") 
                new_acc_nr = ngd_upper_lineage(curr_index_in_lineage,
                                               lineage,
                                               ncbi,
                                               accnrlisttmp, # current working list
                                               accnrlist, # final list, if something added (or min index reached), recursivity stop
                                               speciestmp,
                                               nametmp
                                               )
                if new_acc_nr is None:
                    print(f"No acc_nr found after going up in taxonomy, line {str(sys._getframe().f_lineno)}")
                else:
                    accnrlist.append( new_acc_nr )
                    # print(f"last item added to accnrlist:{accnrlist[-1]}, line {str(sys._getframe().f_lineno)}")
                
                # initialize for next search
                accnrlisttmp = []
                speciestmp   = []
                nametmp      = []
                
            elif not re.match("^Considering", line):
                # print(f"line:{line.rstrip()}")
                acc_nr, species, name = line.rstrip().split("\t")
                accnrlisttmp.append(acc_nr)
                # print(f"last item added to accnrlist:{accnrlist[-1]}, line {str(sys._getframe().f_lineno)}")
                            
                speciestmp.append(species)
                nametmp.append(name)                                  
                if b_verbose:
                    print(f"{prog_tag} we found for {species} chr fasta for host genome with accnr {acc_nr} (name:{name})")

        # retain only the most recent complete genome for current treated taxid
        if len(accnrlisttmp):
            accnrlist.append( retain_1accnr(accnrlisttmp, speciestmp, nametmp) )
            # print(f"last item added to accnrlist:{accnrlist[-1]}, line {str(sys._getframe().f_lineno)}")

    # remove redundant accnr
    print(f"accnrlist to sort:{accnrlist}")
    accnrlist = list(sort_uniq(accnrlist))
    with open(acc_out_f, "w") as record_file:
        for accnr in accnrlist:
            record_file.write("%s\n" % (accnr))
    # ------------------------------------------

    print(f"{prog_tag} {acc_out_f} file created")

# --------------------------------------------------------------------------
# test
if b_test_add_host_chr_taxids_accnr_from_ori_list:
   taxid_acc_in_f = test_dir + 'megablast_out_f_taxid_acc_host.tsv'
   acc_out_f = test_dir + 'megablast_out_f_taxid_acc_hostexpanded.tsv'
   print(f"{prog_tag} START b_test_add_host_chr_taxids_accnr_from_ori_list")
   print(f"{prog_tag} loading {taxid_acc_in_f} file")
   load_taxids(taxid_acc_in_f)
   for i in range(len(taxidlist)):
       print(f"{taxidlist[i]}\t{accnrlist[i]}")
   print(f"{prog_tag} end loading")   
   
   add_host_chr_taxids_accnr_from_ori_list(taxidlist,
                                           accnrlist,
                                           acc_out_f)
   print(f"{prog_tag} END b_test_add_host_chr_taxids_accnr_from_ori_list")
   sys.exit()
# --------------------------------------------------------------------------

# --------------------------------------------------------------------------
# MAIN
# --------------------------------------------------------------------------
##### MAIN
def __main__():
    # load taxid_acc file
    load_taxids(taxid_acc_tabular_f)
    # check in ncbi taxonomy which acc number are in and out of given taxid
    add_host_chr_taxids_accnr_from_ori_list(taxidlist,
                                            accnrlist,                                            
                                            acc_out_f)
    # --------------------------------------------------------------------------
#### MAIN END
if __name__ == "__main__": __main__()
  
