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
from natsort import natsorted
# to find all lineage and in case of no complete genome, the deduction of closests complete genomes (same genus, order...)
from ete3 import NCBITaxa

# to be able to report line number in error messages
import inspect
frame = inspect.currentframe()

# debug
test_dir = 'test_TAXID_genusexpand_taxid2acc_offline_searchinhostcompletegenomedb/'
b_test_load_taxids = False      # ok 2023 09 11 with rm redundant taxid code
b_test_get_host_complete_genome_acc_nr_found   = False # ok 2023 09 11

prog_tag = '[' + os.path.basename(__file__) + ']'

# boolean to know if we dowload ncbi taxonomy file in current env
b_load_ncbi_tax_f = False

# var
#taxid_acc_in_f        = ''
#taxid_acc_hostdb_in_f = ''

# list of interesting taxid (fathers)
taxidlist_f    = ''
taxidlist      = []
accnrlist      = []
taxidlisthosts = []
accnrlisthosts = []
    
# order = -4
# family or clade = -3
# subtribe or genus = -2
curr_index_in_lineage = -1
min_index_in_lineage = -4

# boolean to know if we download ncbi taxonomy file in current env
b_load_ncbi_tax_f = False
b_test_all        = False
b_test            = False
b_acc_in_f        = False
b_acc_hostdb_in_f = False
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
parser.add_argument("-d", "--taxid_acc_hostdb_in_f", dest='taxid_acc_hostdb_in_f',
                    help="taxid acc_number list in tsv (tabular separated at each line) for HOSTS",
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

args = parser.parse_args()

# -------------------------------------------
# check arguments
b_test_all = args.b_test_all

if b_test_all:
    b_test_load_taxids = False
    b_test_get_host_complete_genome_acc_nr_found = True
    b_test = True
    b_acc_in_f = True
    b_acc_hostdb_in_f = True    
    b_acc_out_f = True
else:
    b_test = (b_test_load_taxids or
              b_test_get_host_complete_genome_acc_nr_found)

if ((not b_test)and
    ((len(sys.argv) < 2) or (len(sys.argv) > 7))):
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
                  '-d taxid_accnr_hostdb_list.tsv',
                  '-o accnr_out_list.txt']),"\n\n" ]),
        "For current hostcompletegenome db, taxid_accnr_hostdb_list.tsv file is ../taxid_lists/host_complete_genomes_taxid_accnr.tsv"          
                  )
    parser.print_help()
    print(prog_tag + "[Error] we found "+str(len(sys.argv)) +
          " arguments, exit line "+str(frame.f_lineno))
    sys.exit(0)

# print('args:', args)
# if(not b_test):
if args.ncbi_tax_f is not None:
    # get absolute path in case of files
    ncbi_tax_f = os.path.abspath(args.ncbi_tax_f)
else:
    # ncbi_tax_f = "/nfs/data/db/ete3/taxa.sqlite"
    ncbi_tax_f = os.path.expanduser("~/.etetoolkit/taxa.sqlite")
if args.taxid_acc_in_f is not None:
    taxid_acc_in_f = os.path.abspath(args.taxid_acc_in_f)
    b_acc_in_f = True    
elif(not b_test):
    sys.exit("[Error] You must provide taxid_acc_in_f")
if args.taxid_acc_hostdb_in_f is not None:
    taxid_acc_hostdb_in_f = os.path.abspath(args.taxid_acc_hostdb_in_f)
    b_acc_hostdb_in_f = True    
elif(not b_test):
    sys.exit("[Error] You must provide taxid_acc_hostdb_in_f")
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
    if (not b_acc_in_f) and (not b_acc_out_f) and (not b_acc_hostdb_in_f):
        sys.exit(prog_tag + "[Error] You must provide either --taxid_acc_f <file> and --taxid_acc_hostdb_in_f <file> and -taxid_acc_out_f <file>")

# # store index of the rank expected by user
# rank_num = ranks{ rank }

# --------------------------------------------------------------------------
# to sort uniq, for a list, only need to add list conversion
# --------------------------------------------------------------------------
mapper= map # Python ≥ 3
def sort_uniq(sequence) -> list:
    return mapper(
        operator.itemgetter(0),
        itertools.groupby(sorted(sequence)))
# --------------------------------------------------------------------------

# --------------------------------------------------------------------------
# Procedure load taxid acc list, return taxidlist
# --------------------------------------------------------------------------
def load_taxids(taxid_acc_tabular_f: str,
                taxid_list_l: list,
                accnr_list_l: list,
                # Need to remove identical taxid in megablast res to avoid 
                # thousand times the same search
                # Not needed for host_db_complet_genome_file
                b_rm_duplicated_taxid: bool):

    if not path.exists(taxid_acc_tabular_f):
        sys.exit("Error " + taxid_acc_tabular_f +
                 " file does not exist, line "+ str(sys._getframe().f_lineno) )

    cmd = "cut -f 1,2 "+taxid_acc_tabular_f+" | sort -u "

    for line in os.popen(cmd).readlines():
        if line.rstrip() != "":
            k, v = line.rstrip().split()
            taxid_list_l.append(int(k))
            accnr_list_l.append(v)
            # print(f"last item added to accnr_list_l:{accnr_list_l[-1]}, line {str(sys._getframe().f_lineno)}")
    
    # if asked, keep only non redundant taxids
    if b_rm_duplicated_taxid:
        # create set (uniq taxids)
        taxid_list_uniq_set = set(taxid_list_l)
        # convert to list
        taxid_list_uniq     = list(taxid_list_uniq_set)
        
        if b_test_load_taxids or b_verbose:
            print(f"{prog_tag} [load_taxids] number taxids:{len(taxid_list_l)}, uniq_taxids:{len(taxid_list_uniq)}")
        accnr_list_uniq     = []
        for taxid_s in list(taxid_list_uniq):
            # find index of uniq taxid in the original list of taxid
            taxid_index = taxid_list_l.index(taxid_s)
            # add deduced related first accession number
            accnr_list_uniq.append( accnr_list_l[taxid_index] )
        if b_test_load_taxids or b_verbose:
            print(f"{prog_tag} [load_taxids] number accnrs:{len(accnr_list_l)}, uniq_accnrs:{len(accnr_list_uniq)}")
        # replace original taxid accnr lists by the one with non redundant taxids
        # this syntaxe force copy in original list (write over)
        taxid_list_l[:] = taxid_list_uniq
        accnr_list_l[:] = accnr_list_uniq
        if b_test_load_taxids or b_test:
            print(f"{prog_tag} [load_taxids] FINAL uniq_taxids:{len(taxid_list_l)} uniq_accnrs:{len(accnr_list_l)}")
# --------------------------------------------------------------------------

# test load_taxids function
# display taxidlist, then exit
if b_test_load_taxids:
    taxid_acc_tabular_f = test_dir + 'megablast_out_f_taxid_acc_testrmredundanttaxids.tsv'
    print("START b_test_load_taxids REDUND")
    print("loading "+taxid_acc_tabular_f+" file")
    taxid_list = []
    accnr_list = []
    load_taxids(taxid_acc_tabular_f,
                taxid_list,
                accnr_list,
                True)
    for i in range(len(taxid_list)):
        print(f"{taxid_list[i]}\t{accnr_list[i]}")
    print(f"{prog_tag} [load_taxids] FINAL taxid_list:{len(taxid_list)} accnr_list:{len(accnr_list)}")
    print("END b_test_load_taxids REDUND")
    
    taxid_acc_tabular_f = test_dir + 'megablast_out_f_taxid_acc_host.tsv'
    print("START b_test_load_taxids")
    print("loading "+taxid_acc_tabular_f+" file")
    taxid_list = []
    accnr_list = []
    load_taxids(taxid_acc_tabular_f,
                taxid_list,
                accnr_list,
                False)
    for i in range(len(taxid_list)):
        print(f"{taxid_list[i]}\t{accnr_list[i]}")
    print("END b_test_load_taxids")
    if not b_test_get_host_complete_genome_acc_nr_found:
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
def retain_1accnr(accnrlisttmp: list, 
                  speciestmp: list, 
                  nametmp: list) -> str:

    max_accnr_version  = 0
    curr_accnr_version = 0
    max_accnr_nr       = 0
    curr_accnr_nr      = 0
    kept_accnr_i       = 0
    p = re.compile("(.*?(\d+)\.(\d+))$")

    print(f"{prog_tag} retain_1accnr({accnrlisttmp}, {speciestmp}, {nametmp}), line {str(frame.f_lineno)}")

    for iacc in range(len(accnrlisttmp)):
        m = p.match( accnrlisttmp[iacc] )
        if m:
            curr_accnr = m.group(1)
            curr_accnr_version = int(m.group(3))
            accnr_nr = int(m.group(2))
            # print(f"curr_accnr_version:{curr_accnr_version} accnr_nr:{accnr_nr}, line {str(frame.f_lineno)}")
            if curr_accnr_version > max_accnr_version:
                max_accnr_version = curr_accnr_version
                kept_accnr_i = iacc
                # print(f"{prog_tag} record kept_accnr_i:{kept_accnr_i} for accnr:{curr_accnr}, line {str(frame.f_lineno)}")
            elif(( curr_accnr_version == max_accnr_version)and
                 (curr_accnr_nr > max_accnr_nr)):
                max_accnr_nr = curr_accnr_nr
                kept_accnr_i = iacc
                # print(f"{prog_tag} record kept_accnr_i:{kept_accnr_i} for accnr:{curr_accnr}, line {str(frame.f_lineno)}")
            elif b_verbose:
                print(f"{prog_tag} keep   kept_accnr_i:{kept_accnr_i} for accnr:{curr_accnr}, line {str(frame.f_lineno)}")
            
        else:
            sys.exit(f"{prog_tag} No version found for accnr:{accnrlisttmp[iacc]}, line {str(frame.f_lineno)}")
    print(f"{prog_tag} kept_accnr_i:{kept_accnr_i}, line {str(frame.f_lineno)}")     
    print(f"retained accnr:{accnrlisttmp[kept_accnr_i]}\tspecies:{speciestmp[kept_accnr_i]}\tname:{nametmp[kept_accnr_i]}")
    kept_accn = accnrlisttmp[kept_accnr_i]

    return kept_accn
# --------------------------------------------------------------------------


# --------------------------------------------------------------------------
# Function to find complete genome closely related to current taxid
# goes upper in taxonomy if nothing found until order
# --------------------------------------------------------------------------
def ngd_upper_lineage(curr_index_in_lineage: int,
                      lineage: list,
                      ncbi: NCBITaxa
                      ) -> list:
    print(f"{prog_tag} [ngd_upper_lineage] with curr_index_in_lineage:{curr_index_in_lineage}")
    
    leaves_taxids_ints = []
    
    # deduce up rank, search complet genome/chr in
    upper_taxid=str(lineage[curr_index_in_lineage]) # order when last is species
    rank = ncbi.get_rank([lineage[curr_index_in_lineage]])
    name = ncbi.get_taxid_translator([lineage[curr_index_in_lineage]])
    print(f"{prog_tag} [ngd_upper_lineage] test with taxid:{upper_taxid} corresponding to rank:{rank}")
    leaves_taxids_ints = ncbi.get_descendant_taxa(upper_taxid,
                                             intermediate_nodes=False,
                                             collapse_subspecies=False,
                                             return_tree=False
                                             )

    # int conversion to strings
    leaves_taxids = list(map(str, leaves_taxids_ints))
    leaves_taxids_list = ','.join(leaves_taxids)

    if b_verbose:
        print(f"{prog_tag} [ngd_upper_lineage] number leaves_taxids returned for taxid {upper_taxid}:{len(leaves_taxids)}")          
    return leaves_taxids_ints   
    
    
# --------------------------------------------------------------------------

# ----------------------------------------------------------------------
# Function that Intersect 2 lists of taxids:
# - host_complete_genome_taxids
#   (host_complete_genome_acc_numbers = acc numbers related to host_complete_genome_taxids: same index pos)
# - leaves_taxids (taxids where we search for host complete genome taxids)

# - record taxid/accnr found in both
# - get not_found_taxids: taxids not found in host complet genome taxids
# - get uppertaxid for not_found_taxids by running ngd_upper_lineage
 
# Return host_complete_genomes_acc_nr, the list of complete genome acc number found related to leaves_taxids
# ----------------------------------------------------------------------    
def get_host_complete_genome_acc_nr_found(  host_complete_genome_taxids: list,
                                            host_complete_genome_acc_numbers: list,
                                            leaves_taxids: list,     
                                            # for further taxonomy analysis
                                            curr_index_in_lineage: int,
                                            lineage: list,
                                            ncbi: NCBITaxa) -> list:
    
    # -------------------------------------------------------------------------
    # part shared for all taxid searched (comparison to host taxids from db)
    
    # initi local working var
    host_complete_genomes_acc_nr = []        # result
    host_complete_genomes_acc_nr_set = set() # result (set)

    # get host complete genomes as a set
    host_complete_genome_taxids_set = set() # knwown host complete genomes
    for host_taxid in host_complete_genome_taxids:
        host_complete_genome_taxids_set.add(host_taxid)
    # -------------------------------------------------------------------------
    
    print(f"{prog_tag} [get_host_complete_genome_acc_nr_found] curr_index_in_lineage:{curr_index_in_lineage} treating {len(leaves_taxids)} taxid(s):{leaves_taxids[0]}...")
        
    # get result taxids as a set
    leaves_taxids_set = set() # taxid found in results
    for res_taxid in leaves_taxids:
        leaves_taxids_set.add(res_taxid)

    print(f"{prog_tag} We intersect:{len(host_complete_genome_taxids)} host complete genomes with")
    #\n{host_complete_genome_taxids}\n
    print(f"{prog_tag}             :{len(leaves_taxids)} genomes in result, line {str(frame.f_lineno)}")
    #\n{leaves_taxids}")

    # do intersection for taxids shared (host complete genomes found in results)
    host_complete_genomes_taxids_intersect_leaves_set = leaves_taxids_set.intersection(host_complete_genome_taxids_set)
    host_complete_genomes_taxids_intersect_leaves_list = list(host_complete_genomes_taxids_intersect_leaves_set)

    if b_verbose:
        print(f"{prog_tag} After intersec, we retain set :{len(host_complete_genomes_taxids_intersect_leaves_set)} taxid to get related acc nr, line {str(frame.f_lineno)}") 
        #\n{host_complete_genomes_taxids_intersect_leaves_set}")
        print(f"{prog_tag} After intersec, we retain list:{len(host_complete_genomes_taxids_intersect_leaves_list)} taxid to get related acc nr, line {str(frame.f_lineno)}")
        #\n{host_complete_genomes_taxids_intersect_leaves_list}")
        
        # get taxid not found to go up in taxonomy, get leave taxids again and cross again with 
        # available taxid/accnr found in hot complete genome db
        not_found_taxids_set = list(leaves_taxids_set.difference(host_complete_genomes_taxids_intersect_leaves_set))
        print(f"{prog_tag} Number of not_found_taxids:{len(not_found_taxids_set)}")
    
    # get index of retained taxids in original host_complete_genome_taxids to deduce related acc numbers
    try:
        # -----------------------------------------------------------
        # search indices of elements of host_complete_genomes_taxids_list in host_complete_genome_taxids
        host_complete_genomes_taxids_indexes = []
        for elt in host_complete_genomes_taxids_intersect_leaves_list:
            host_complete_genomes_taxids_indexes.append(host_complete_genome_taxids.index(elt))
        # -----------------------------------------------------------
        if len(host_complete_genomes_taxids_intersect_leaves_list) != len(host_complete_genomes_taxids_indexes):
            sys.exit(f"{prog_tag} number of indexes retained != number of taxids retained: NOT NORMAL, line {str(frame.f_lineno)}")
        # print(f"{prog_tag} After intersec, nr indexes retained: {len(host_complete_genomes_taxids_indexes)}, line {str(frame.f_lineno)}")  

        # get acc numbers, sorted
        host_complete_genomes_acc_nr = natsorted( [ host_complete_genome_acc_numbers[i] for i in host_complete_genomes_taxids_indexes ] )
        print(f"{prog_tag} After intersec, nr accnr retained: {len(host_complete_genomes_acc_nr)}, line {str(frame.f_lineno)}")  
        
        if len(host_complete_genomes_acc_nr) == 0:
            print(f"no acc nr found for provided leaves_taxids_ints, line {str(frame.f_lineno)}")
        elif len(host_complete_genomes_acc_nr) == 1:
            accnr = host_complete_genomes_acc_nr
            taxid = host_complete_genomes_taxids_intersect_leaves_list
            name = list(ncbi.get_taxid_translator(host_complete_genomes_taxids_intersect_leaves_list).values())
            species = name
            print(f"retained accnr:{accnr}\tspecies:{species}\tname:{name}, line {str(frame.f_lineno)}")
            return host_complete_genomes_acc_nr
        elif len(host_complete_genomes_acc_nr) > 1:
            accnrlisttmp = host_complete_genomes_acc_nr
            nametmp = list(ncbi.get_taxid_translator(host_complete_genomes_taxids_intersect_leaves_list).values())
            speciestmp = nametmp
            print(f"{prog_tag} retain_1accnr in {accnrlisttmp}, line {str(frame.f_lineno)}")
            return retain_1accnr(accnrlisttmp, speciestmp, nametmp)
        else:
            sys.exit(f"{prog_tag} [Error] Case not treated len of found_complete_genomes:{len(host_complete_genomes_acc_nr)}, curr_index_in_lineage:{curr_index_in_lineage}, line {str(frame.f_lineno)}")

    except ValueError:
        """
        # specific to retain_1accn to avoid lists are crashed by other ngd call
        accnrlisttmp_r = []
        speciestmp_r   = []
        nametmp_r      = []
        """

        # goes up in taxonomy to get a larger number of taxids to cross with host genome taxids
        if( (len(host_complete_genomes_acc_nr) == 0) and (curr_index_in_lineage > min_index_in_lineage)):
            curr_index_in_lineage = curr_index_in_lineage - 1
            upper_taxid = lineage[curr_index_in_lineage]
            rank = ncbi.get_rank(upper_taxid[curr_index_in_lineage])
            print(f"{prog_tag} No chr/complete genome for taxid:{upper_taxid} rank:{rank} (expanding name:{name}), line {str(frame.f_lineno)}")
            if b_verbose:
                print(f"{prog_tag} ngd_upper_lineage call {curr_index_in_lineage} line {str(sys._getframe().f_lineno)}") 
            
            # get complete lineage: accept ONLY leave taxid? (species)
            # name = ncbi.get_taxid_translator(upper_taxid)
            if b_verbose:
                print(f"taxid:{upper_taxid}\tlineage:{lineage}\tname:{name}")
            leave_taxid_ints = ngd_upper_lineage(  curr_index_in_lineage,
                                lineage,
                                ncbi                                   
                                )
                    # we search if one of the accession numbers of complete genome is included in leaves_taxids_ints  
            if b_verbose:
                print(f"{prog_tag} get_host_complete_genome_acc_nr_found(\nhost_complete_genome_taxids,\nhost_complete_genome_acc_numbers,\nleaves_taxids_ints) ran")

            found_complete_genomes = get_host_complete_genome_acc_nr_found(
                host_complete_genome_taxids,
                host_complete_genome_acc_numbers,
                leave_taxid_ints,
                # for further taxonomy analysis
                curr_index_in_lineage,
                lineage,
                ncbi)      
        
        # retain only the most recent complete genome for current treated taxid
        # return retain_1accnr(accnrlisttmp_r, speciestmp_r, nametmp_r)
        elif len(host_complete_genomes_acc_nr) == 0:
            print(f"no acc nr found for provided leaves_taxids_ints, line {str(frame.f_lineno)}")
            return ''
        elif len(host_complete_genomes_acc_nr) == 1:
            print(f"retained accnr:{accnr}\tspecies:{species}\tname:{name}, line {str(frame.f_lineno)}")
            return host_complete_genomes_acc_nr
        elif len(host_complete_genomes_acc_nr) > 1:
            accnrlisttmp = host_complete_genomes_acc_nr
            speciestmp = list(ncbi.get_taxid_translator(host_complete_genomes_taxids_intersect_leaves_list).values())
            nametmp = speciestmp
            print(f"{prog_tag} retain_1accnr in {accnrlisttmp}, line {str(frame.f_lineno)}")
            return retain_1accnr(accnrlisttmp, speciestmp, nametmp)
        else:
            sys.exit(f"{prog_tag} [Error] Case not treated len of found_complete_genomes:{len(host_complete_genomes_acc_nr)}, curr_index_in_lineage:{curr_index_in_lineage}, line {str(frame.f_lineno)}")


    # goes up in taxonomy to get a larger number of taxids to cross with host genome taxids
    if( (len(host_complete_genomes_acc_nr) == 0) and (curr_index_in_lineage > min_index_in_lineage)):
        curr_index_in_lineage = curr_index_in_lineage - 1
        upper_taxid_int = lineage[curr_index_in_lineage]
        upper_taxid = str(upper_taxid_int)
        rank = ncbi.get_rank([upper_taxid_int])
        name = ncbi.get_taxid_translator([upper_taxid_int])
        print(f"{prog_tag} No chr/complete genome for taxid:{upper_taxid} rank:{rank} (expanding name:{name}), line {str(frame.f_lineno)}")
        if b_verbose:
            print(f"{prog_tag} ngd_upper_lineage call {curr_index_in_lineage} line {str(sys._getframe().f_lineno)}") 
        
        # get complete lineage: accept ONLY leave taxid? (species)
        if b_verbose:
            print(f"taxid:{upper_taxid}\tlineage:{lineage}\tname:{name}")
            
        # get taxids for current lineage up some lines earlier, we want to get leave taxids for this species/group/genus/family etc...
        leave_taxid_ints = ngd_upper_lineage(  curr_index_in_lineage,
                            lineage,
                            ncbi
                            )
        print(f"{prog_tag} number of leave_taxid_ints obtained for rank:{rank}: {len(leave_taxid_ints)}, line {str(frame.f_lineno)}")
        
        # we search if one of the accession numbers of complete genome is included in leaves_taxids_ints  
        if b_verbose:
            print(f"{prog_tag} get_host_complete_genome_acc_nr_found(\nhost_complete_genome_taxids,\nhost_complete_genome_acc_numbers,\nleaves_taxids_ints) ran")

        found_complete_genomes = get_host_complete_genome_acc_nr_found(
            host_complete_genome_taxids,
            host_complete_genome_acc_numbers,
            leave_taxid_ints,
            # for further taxonomy analysis
            curr_index_in_lineage,
            lineage,
            ncbi)         


    
if b_test_get_host_complete_genome_acc_nr_found:
    taxid_acc_in_f = test_dir + 'megablast_out_f_taxid_acc_host.tsv'
    taxid_acc_hostdb_in_f = test_dir + 'host_complete_genomes_taxid_accnr.tsv'
    # taxid_u = ['4520','4530','9606']
    # we must obtain retained 
    # accnr:GCF_022539505.1	species:Lolium rigidum	name:na
    # accnr:GCF_000231095.2	species:Oryza brachyantha	name:na
    # accnr:GCF_000001405.40	species:Homo sapiens	name:na
    taxid_u = [126889,4520,4530,9187,9606]
    
    # taxid_u = [4530] # oriza
    
    # load taxid_acc file
    load_taxids(taxid_acc_in_f,
                taxidlist,
                accnrlist,
                True) # remove redundant taxids

    # load host db taxid acc
    load_taxids(taxid_acc_hostdb_in_f,
                taxidlisthosts,
                accnrlisthosts,
                False) # no need to remove redundant taxids
    
    # load NCBITaxa
    ncbi = NCBITaxa()   # Install ete3 db in local user file (.ete_toolkit/ directory)
    print(prog_tag + " Try to load ncbi tax db file:"+ncbi_tax_f)
    ncbi = NCBITaxa(dbfile=ncbi_tax_f)
    if (not os.path.isfile(ncbi_tax_f)) or b_load_ncbi_tax_f:
        try:
            ncbi.update_taxonomy_database()
        except:
            warnings.warn(prog_tag+"[SQLite Integrity error/warning] due to redundant IDs")

    print(f"{prog_tag} [TEST get_host_complete_genome_acc_nr_found] START")
    # check in ncbi taxonomy which acc number are in and out of given taxid
    
    accnrlisttmp = []
    for glob_taxid in taxid_u:

        # important
        curr_index_in_lineage = -1

        # get complete lineage: accept ONLY leave taxid? (species)
        lineage = ncbi.get_lineage(glob_taxid)
        # get species and names
        # accnrlisttmp = acc nr of found complete genomes
        nametmp = list(ncbi.get_taxid_translator(lineage).values())
    
        print(f"{prog_tag} We search for host complete genome related to taxid:{glob_taxid}\tname:{nametmp}")

        accnrlisttmp.append( 
                        get_host_complete_genome_acc_nr_found(
                            taxidlisthosts,
                            accnrlisthosts,
                            [glob_taxid],
                            # for further taxonomy analysis
                            curr_index_in_lineage,
                            lineage,
                            ncbi)     
    )
    print(f"{prog_tag} [TEST get_host_complete_genome_acc_nr_found] END")
    sys.exit()
# ----------------------------------------------------------------------

# --------------------------------------------------------------------------
# MAIN
# --------------------------------------------------------------------------
##### MAIN
def __main__():
    
    # load taxid_acc file
    load_taxids(taxid_acc_in_f,
                taxidlist,
                accnrlist,
                True) # remove redundant taxids (avoid to search n times the same acc nr)

    # load host db taxid acc
    load_taxids(taxid_acc_hostdb_in_f,
                taxidlisthosts,
                accnrlisthosts,
                False) # do not try to remove redundancy, there is no redundant taxid in db
    
    # load NCBITaxa
    ncbi = NCBITaxa()   # Install ete3 db in local user file (.ete_toolkit/ directory)
    print(prog_tag + " Try to load ncbi tax db file:"+ncbi_tax_f)
    ncbi = NCBITaxa(dbfile=ncbi_tax_f)
    if (not os.path.isfile(ncbi_tax_f)) or b_load_ncbi_tax_f:
        try:
            ncbi.update_taxonomy_database()
        except:
            warnings.warn(prog_tag+"[SQLite Integrity error/warning] due to redundant IDs")

    # global final results: accnrlist
    accnrlist_res = []
    
    # for each taxid found in res
    for taxid_u in taxidlist:

        # get complete lineage: accept ONLY leave taxid? (species)
        lineage = ncbi.get_lineage(int(taxid_u))
        # get species and names
        # accnrlisttmp = acc nr of found complete genomes
        nametmp = ncbi.translate_to_names(lineage)
        
        taxid_u_l = [taxid_u]
        
        """
        speciestmp = ''
        # get species name
        for taxid in lineage.reversed:
            if ncbi.get_rank(taxid) == 'species':
                speciestmp = ncbi.get_taxid_translator(taxid)
                break
        """
            
        if b_verbose:
            print(f"taxid:{taxid_u}\tlineage:{lineage}\tname:{nametmp}")

        try:
            # check in ncbi taxonomy which acc number are in and out of given taxid
            accnrlisttmp = get_host_complete_genome_acc_nr_found(
                        taxidlisthosts,
                        accnrlisthosts,
                        taxid_u_l,
                        # for further taxonomy analysis
                        curr_index_in_lineage,
                        lineage,
                        ncbi)     
            accnrlist_res.extend(accnrlisttmp)
        except TypeError as nterr:
            print(f"{prog_tag} Nothing return for global taxid:{taxid_u}")
            
        
        """
        # retain only the most recent complete genome for current treated taxid
        if len(accnrlisttmp):
            accnrlist_res.append( retain_1accnr(accnrlisttmp, speciestmp, nametmp) )
            # print(f"last item added to accnrlist:{accnrlist[-1]}, line {str(sys._getframe().f_lineno)}")
        """                      
    # remove redundant accnr
    print(f"accnrlist_res to sort:{accnrlist_res}")
    accnrlist_res = list(sort_uniq(accnrlist_res))
    with open(acc_out_f, "w") as record_file:
        for accnr in accnrlist_res:
            record_file.write("%s\n" % (accnr))
    # ------------------------------------------

    print(f"{prog_tag} {acc_out_f} file created")
    
    """
    add_host_chr_taxids_accnr_from_ori_list(taxidlist,
                                            accnrlist,                                            
                                            acc_out_f,
                                            taxidlisthosts,
                                            accnrlisthosts)
    """
    # --------------------------------------------------------------------------
#### MAIN END
if __name__ == "__main__": __main__()
  
