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
import argparse, os, sys, csv, warnings, re
from os import path
# from natsort import natsorted
import ncbi_genome_download as ngd

# to be able to report line number in error messages
import inspect
frame = inspect.currentframe()

# debug
b_test_load_taxids = False                            # ok 2023 03 07
b_test_add_host_chr_taxids_accnr_from_ori_list = True # ok 2023 03 07

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
parser.add_argument("-i", "--taxid_acc_in_f", dest='taxid_acc_in_f',
                    help="taxid acc_number list in tsv (tabular separated at each line)",
                    metavar="FILE")
parser.add_argument("-o", "--acc_out_f", dest='acc_out_f',
                    help="[optional if --taxid_acc_in_f provided] Output text file with accession numbers from krona_taxid_acc_f NOT found under taxid in ncbi taxonomy tree",
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
                                "conda activate TAXID_genusexpand_taxid2acc",
                                " ",
                                "Then, as an example:\n",
                     ' '.join(['./TAXID_genusexpand_taxid2acc.py',
                                                  '-i taxid_accnr_list.tsv',
                                                  '-o accnr_out_list.txt']),"\n\n" ]))
    parser.print_help()
    print(prog_tag + "[Error] we found "+str(len(sys.argv)) +
          " arguments, exit line "+str(frame.f_lineno))
    sys.exit(0)

# print('args:', args)
# if(not b_test):
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
# load taxid acc list, return taxidlist
# --------------------------------------------------------------------------
def load_taxids(taxid_acc_tabular_f):

    if not path.exists(taxid_acc_tabular_f):
        sys.exit("Error " + taxid_acc_tabular_f +
                 " file does not exist, line "+ str(sys._getframe().f_lineno) )

    cmd = "cut -f 1,2 "+taxid_acc_tabular_f+" | sort | uniq "
    # cmd = "cut -f 1 "+taxid_acc_tabular_f+" | sort | uniq "

    for line in os.popen(cmd).readlines():
        k, v = line.rstrip().split()
        taxidlist.append(k)
        accnrlist.append(v)

    return taxidlist
# --------------------------------------------------------------------------

# test load_taxids function
# display taxidlist, then exit
if b_test_load_taxids:
    taxid_acc_tabular_f = 'megablast_out_f_taxid_acc_host.tsv'
    print("START b_test_load_taxids")
    print("loading "+taxid_acc_tabular_f+" file")
    taxidlist = load_taxids(taxid_acc_tabular_f)
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
# read taxids, deduce complete genomes available in genblank, provides in output file
# the acc number in addition  to those already listed
# --------------------------------------------------------------------------
def add_host_chr_taxids_accnr_from_ori_list(taxidlist,
                                            acc_out_f):
    # get host complete genome when found using ncbi_genome_download
    taxids_list=','.join(taxidlist)

    # # ------------------------------------------
    # # ncbi-genome-download as a library
    # ngd_out_f= os.getcwd()+'/accnr_sp_accnr.tsv'
    # ngd.download(section='genbank',
    #              taxids=taxids_list,
    #              assembly_levels='chromosome',
    #              flat_output=True,
    #              output=ngd_out_f,
    #              groups='vertebrate_other,vertebrate_mammalian,plant,invertebrate',
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
    cmd = f"ncbi-genome-download -s genbank --taxids {taxids_list} --assembly-level chromosome --dry-run vertebrate_other,vertebrate_mammalian,plant,invertebrate"
    for line in os.popen(cmd).readlines():
        if not re.match("^Considering", line):
            if b_verbose:
                print(f"line:{line.rstrip()}")
            acc_nr, species, name = line.rstrip().split("\t")
        # if acc_nr != 'Considering':
            accnrlist.append(acc_nr)
            if b_verbose:
                print(f"{prog_tag} we found for {species} chr fasta for host genome with accnr {acc_nr} (name:{name})")

    with open(acc_out_f, "w") as record_file:
        for accnr in accnrlist:
            record_file.write("%s\n" % (accnr))
    # ------------------------------------------

    print(f"{prog_tag} {acc_out_f} file created")

# --------------------------------------------------------------------------
# test
if b_test_add_host_chr_taxids_accnr_from_ori_list:
   taxid_acc_tabular_f = 'megablast_out_f_taxid_acc_host.tsv'
   taxid_acc_in_f = 'megablast_out_f_taxid_acc_host.tsv'
   acc_out_f = 'megablast_out_f_taxid_acc_hostexpanded.tsv'
   print(f"{prog_tag} START b_test_add_host_chr_taxids_accnr_from_ori_list")
   print(f"{prog_tag} loading {taxid_acc_tabular_f} file")
   taxidlist = load_taxids(taxid_acc_in_f)
   print(f"{prog_tag} end loading")   
   
   add_host_chr_taxids_accnr_from_ori_list(taxidlist,
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
                                            acc_out_f)
    # --------------------------------------------------------------------------
#### MAIN END
if __name__ == "__main__": __main__()
  
