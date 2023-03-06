#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###
# USE PYTHON3
# From a file of accession numbers, deduce equivalent taxids, deduce related genus taxids, traduc it to species accession number ideally only with complete genomes (chromosomes)
# provide 2 files:
# - file with all acc numbers that are included in taxid(s) provided by user (extended to genus level)
# - file with all acc numbers that are excluded in taxid(s) provided by user (extended to genus level)
###

### Libraries to import:
import argparse, os, sys, csv, warnings
from os import path
# from natsort import natsorted
import ncbi_genome_download as ngd

# to be able to report line number in error messages
import inspect
frame = inspect.currentframe()

# debug
b_test_load_taxids = True #
b_test_add_host_chr_taxids_accnr_from_ori_list = True

prog_tag = '[' + os.path.basename(__file__) + ']'

# list of interesting taxid (fathers)
taxidlist_f = ''
taxidlist = []
accnrlist = []

# boolean to know if we download ncbi taxonomy file in current env
b_load_ncbi_tax_f = False
b_test_all        = False
b_test            = False
b_acc_in_f        = False
b_acc_out_f       = False

b_verbose         = False

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
parser.add_argument("-i", "--acc_in_f", dest='acc_in_f',
                    help="acc number list",
                    metavar="FILE")
parser.add_argument("-o", "--acc_out_f", dest='acc_out_f',
                    help="[optional if --acc_in_f provided] Output text file with accession numbers from krona_taxid_acc_f NOT found under taxid in ncbi taxonomy tree",
                    metavar="FILE")
# parser.add_argument("-r", "--rank", dest='rank',
#                     help="[Optional] default: genus, rank to retain for each acc number provided. We will retain all the acc number descendant from this 'rank' (genus) taxid list",
#                     action="store_const")
# parser.add_argument("-l", "--load_ncbi_tax_f", dest='b_load_ncbi_tax_f',
#                     help="[Optional] load ncbi tabular file with taxonomy organized to represent a tree in current env at default location (~/.etetoolkit/taxa.sqlite). Only needed for first run",
#                     action='store_true')
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
    b_test_load_taxids = True
    b_test_add_host_chr_taxids_accnr_from_ori_list = True 
    b_test = True
    b_acc_in_f = True
    b_acc_out_f = True
else:
    b_test = (b_test_load_taxids or
              b_test_add_host_chr_taxids_accnr_from_ori_list)

if ((not b_test)and
    ((len(sys.argv) < 1) or (len(sys.argv) > 5))):
    print("\n".join(["To use this scripts, run:",
                                "conda activate MEGABLAST_TAB_select_acc_under_taxids",
                                "./TAXID_genusexpand_taxid2acc.py --load_ncbi_tax_f",
                                " ",
                                "Then you won't need --load_ncbi_tax_f options\n\n",
                     "Example: "+ ' '.join(['./TAXID_genusexpand_taxid2acc.py',
                                                  '-i accnr_list.txt',
                                                  '-r megablast_out_f_taxid_acc.tsv',
                                                  '-o genus']),"\n\n" ]))
    parser.print_help()
    print(prog_tag + "[Error] we found "+str(len(sys.argv)) +
          " arguments, exit line "+str(frame.f_lineno))
    sys.exit(0)

# print('args:', args)
# if(not b_test):
if args.acc_in_f is not None:
    acc_in_f = os.path.abspath(args.acc_f)
    b_acc_in_f = True    
elif(not b_test):
    sys.exit("[Error] You must provide acc_in_f")
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
# load taxid acc list, return taxidlist
# --------------------------------------------------------------------------
def load_taxids(taxid_acc_tabular_f):

    if not path.exists(taxid_acc_tabular_f):
        sys.exit("Error " + taxid_acc_tabular_f +
                 " file does not exist, line "+ str(sys._getframe().f_lineno) )

    # cmd = "cut -f 1,2 "+taxid_acc_tabular_f+" | sort | uniq "
    cmd = "cut -f 1 "+taxid_acc_tabular_f+" | sort | uniq "

    for line in os.popen(cmd).readlines():
        taxidlist.append(line.rstrip())

    return taxidlist
# --------------------------------------------------------------------------

# test load_taxids function
# display taxidlist, then exit
if b_test_load_taxids:
    taxid_acc_tabular_f = 'megablast_out_f_taxid_acc.tsv'
    print("START b_test_load_taxids")
    print("loading "+taxid_acc_tabular_f+" file")
    taxidlist = load_taxids(taxid_acc_tabular_f)
    for k in taxidlist:
        print(k)
    print("END b_test_load_taxids")
    if not b_test_add_host_chr_taxids_accnr_from_ori_list:
        sys.exit()
# --------------------------------------------------------------------------

def get_leave_taxid_from_acc_nr(accnrlist):

    # deduce a list of taxid from a list of accession numbers
    cmd = "cat megablast_out_f_acc_out_taxid.tsv | epost -db nuccore | esummary | xtract -pattern DocumentSummary -element TaxId | sort -u"
    for line in os.popen(cmd).readlines():
        taxidlist.append(line.rstrip())

    return taxidlist


def add_host_chr_taxids_accnr_from_ori_list(taxidlist,
                                            acc_out_f):
    # get host complete genome when found using ncbi_genome_download
    # cmd = "ncbi-genome-download -s genbank --taxids 126889,9606,4530 --assembly-level chromosome --dry-run vertebrate_other,vertebrate_mammalian,plant,invertebrate"
    # acc_nr, species, acc_nr_bis = `cmd`
    taxids_list=','.join(taxidlist)
    acc_nr, species, acc_nr_bis = ngd.download(section='genbank',
                                               taxids=taxids_list,
                                               assembly_levels='chromosome',
                                               output='out', 
                                               groups='vertebrate_other,vertebrate_mammalian,plant,invertebrate',
                                               dry_run=True                                                           
                                            )

    accnum_list.append(acc_nr)
    for i in range(length(acc_nr)):
        accocc_list.append('100')
        
    if b_verbose:
        print(prog_tag + " we found "+ str(length(species)) + " chr fasta for host genome "+ ','.join(species))

    print(prog_tag + acc_out_f + " file created")

if b_test_add_host_chr_taxids_accnr_from_ori_list:
   acc_in_f = 'megablast_out_f_taxid_acc.tsv'
   acc_out_f = 'megablast_out_f_taxid_acc_expanded.tsv'
   print("START b_test_add_host_chr_taxids_accnr_from_ori_list")
   print("loading "+taxid_acc_tabular_f+" file")
   taxidlist = load_taxids(acc_in_f)
   print("end loading")   
   
   add_host_chr_taxids_accnr_from_ori_list(taxidlist,
                                           acc_out_f)
   print("END b_test_add_host_chr_taxids_accnr_from_ori_list")   
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
                                            acc_out_f)
    # --------------------------------------------------------------------------
#### MAIN END
if __name__ == "__main__": __main__()
  
