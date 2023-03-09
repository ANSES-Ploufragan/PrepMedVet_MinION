#!/usr/bin/env python
# -*- coding: utf-8 -*-
###
# From taxid file (one taxid a line)
# deduce species taxids related
###

### Libraries to import:
# USE PYTHON3
import argparse, os, sys, csv, warnings
from ete3 import NCBITaxa
from os import path
from natsort import natsorted

# to be able to report line number in error messages
import inspect
frame = inspect.currentframe()

# debug
b_test_creates_sp_taxid_f_from_taxid_f = False # ok 2022 08 19

prog_tag = '[' + os.path.basename(__file__) + ']'

# list of interesting taxid (fathers)
taxidlist_f = ''
taxidlist = []

# taxid found under the taxid searched for
tax_in = []

# boolean to know if we dowload ncbi taxonomy file in current env
b_load_ncbi_tax_f = False
b_verbose = False
b_test_all = False
b_test = False
ncbi_tax_f = os.path.expanduser("~/.etetoolkit/taxa.sqlite")

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--taxid_in_f", dest='taxid_in_f',
                    help="taxid list (genus, order, species, whichever type)",
                    metavar="FILE")
parser.add_argument("-o", "--taxid_out_f", dest='taxid_out_f',
                    help="Output text file with species taxid found in or under all taxids in the taxid_in_f file",
                    metavar="FILE")
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

args = parser.parse_args()

# -------------------------------------------
# check arguments
b_test_all = args.b_test_all

if b_test_all:
    b_test_creates_sp_taxid_f_from_taxid_f = True
    b_test = True
else:
    b_test = b_test_creates_sp_taxid_f_from_taxid_f

if ((not b_test)and
    ((len(sys.argv) < 5) or (len(sys.argv) > 8))):
    print("\n".join(["To use this scripts, install first TAXID_get_sp_taxid_from_taxid_list.yaml conda env. Then run:",
                                "conda activate TAXID_get_sp_taxid_from_taxid_list",
                                "\n\n",
                     "Example: "+ ' '.join(['./MEGABLAST_TAB_get_taxid_acc.py',
                                                  '-i general_taxid_in.txt',
                                                  '-o sp_taxid_out.txt']),"\n\n" ]))
    parser.print_help()
    print(prog_tag + "[Error] we found "+str(len(sys.argv)) +
          " arguments, exit line "+str(frame.f_lineno))
    sys.exit(0)

# print('args:', args)
if(not b_test):
    if args.taxid_in_f is not None:
        # get absolute path in case of files        
        taxid_in_f = os.path.abspath(args.taxid_in_f)
        taxidlist_f_handle = open(tax_in_f, "r")
        for line in taxidlist_f_handle:
            line = line.rstrip()
            taxidlist.append(line)
        taxidlist_f_handle.close()
    else:
        sys.exit("[Error] You must provide taxid_in_f")
    if args.taxid_out_f is not None:
        taxid_out_f = os.path.abspath(args.taxid_out_f)

# ------------------------------------------------------------------------
# from a taxid_in_f file with genral taxid (species, ordre, genus, etc), returns a file with only
# species taxid
# output file name provided as parameter
# ------------------------------------------------------------------------
krona_taxid_acc_f = ''
def creates_sp_taxid_f_from_taxid_f(taxidlist,    # list of taxids under which we search for species taxid
                                    ncbi_tax_f,   # ncbi taxonomy file, browsed to find taxid, then taxid/acc under
                                    taxid_out_f): # species taxid list

    if not path.exists(ncbi_tax_f):
        warnings.warn(prog_tag + "[Warn] "+ ncbi_tax_f+
                 " file does not exist, line "+ str(sys._getframe().f_lineno) )

    print(prog_tag + " List of given taxid"+str(taxidlist))

    ncbi = NCBITaxa()   # Install ete3 db in local user file (.ete_toolkit/ directory)
    print(prog_tag + " Try to load ncbi tax db file:"+ncbi_tax_f)
    ncbi = NCBITaxa(dbfile=ncbi_tax_f)
    if (not os.path.isfile(ncbi_tax_f)) or b_load_ncbi_tax_f:
        try:
            ncbi.update_taxonomy_database()
        except:
            warnings.warn(prog_tag+"[SQLite Integrity error/warning] due to redundant IDs")

    all_tax_extract = set()
    for tax in taxidlist:
        # print("Tax id extracted now:"+tax)
        all_tax_extract.add(str(tax))
        # intermediate set to false because we want only species taxid in output
        list_tax = ncbi.get_descendant_taxa(tax, intermediate_nodes=False)
        list_tax.sort()
        # print("Length of tax extracted:"+str(len(list_tax)))
        for taxl in list_tax:
            all_tax_extract.add(str(taxl))
            
    # # verif ok
    # print("all_tax_extract:")
    # print(', '.join(natsorted(all_tax_extract)))
    # sys.exit("all_tax_extract check end")


    # get all species taxid sorted
    tax_in = natsorted(list(all_tax_extract))

    # # verif ok
    # print("tax_in:")
    # print(', '.join(tax_in))
    # sys.exit("tax_in check end")


    # ints conversion to strings
    tax_in = list(map(str, tax_in))

    # write only species taxids
    taxid_out_f_handle = open(taxid_out_f, "w")
    taxid_out_f_handle.write("\n".join(tax_in))
    taxid_out_f_handle.write("\n")
    if b_verbose:
        print(prog_tag + " record acc in :"+",".join(tax_in)+" from taxids:"+",".join(tax_in))

    taxid_out_f_handle.close()
    print(prog_tag + ' '+ taxid_out_f+" file created")

# test creates_sp_taxid_f_from_taxid_f function
# display created file and header
if b_test_creates_sp_taxid_f_from_taxid_f:
    # ncbi_tax_f = os.path.expanduser("~/.etetoolkit/taxa.sqlite") # set at the beginning of the prog
    taxid_in_f = 'general_taxid_in.txt'
    print(prog_tag + " START b_test_creates_sp_taxid_f_from_taxid_f")
    print(prog_tag + " loading "+taxid_in_f+" file")
    taxidlist_f_handle = open(taxid_in_f, "r")
    for line in taxidlist_f_handle:
        line = line.rstrip()
        taxidlist.append(line)
    taxidlist_f_handle.close()
    
    taxid_out_f = 'sp_taxid_out.txt'
    creates_sp_taxid_f_from_taxid_f(taxidlist,    # list of taxids under which we search for species taxid
                                    ncbi_tax_f,   # ncbi taxonomy file, browsed to find taxid, then taxid/acc under
                                    taxid_out_f)
    if os.path.isfile(taxid_out_f):
        print(prog_tag + " " + taxid_out_f + " file created, start with:")
        cmd = "head " + taxid_out_f
        print(os.system(cmd))
    else:
        sys.exit(prog_tag + "[Error] creates_sp_taxid_f_from_taxid_f has not created file "+taxid_out_f)
    print("END b_test_creates_sp_taxid_f_from_taxid_f")
    sys.exit("Exit program after test")

# --------------------------------------------------------------------------

# --------------------------------------------------------------------------
# MAIN
# --------------------------------------------------------------------------
##### MAIN
def __main__():
    # creates sp taxid list from general taxid list
    creates_sp_taxid_f_from_taxid_f(taxidlist,    # list of taxids under which we search for species taxid
                                    ncbi_tax_f,   # ncbi taxonomy file, browsed to find taxid, then taxid/acc under
                                    taxid_out_f)

#### MAIN END
if __name__ == "__main__": __main__()
  
