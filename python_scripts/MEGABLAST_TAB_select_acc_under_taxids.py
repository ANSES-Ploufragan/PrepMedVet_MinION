#!/usr/bin/env python
# -*- coding: utf-8 -*-
###
# From a taxid add file of results (output of MEGABLAST_TAB_get_acc_taxid.py) and taxid(s) user is interested in,
# provide 2 files:
# - file with all acc numbers in megablast results that are included in taxid(s) provided by user
# - file with all acc numbers in megablast results that are excluded in taxid(s) provided by user
###

### Libraries to import:
import argparse, os, sys, csv, warnings
from ete3 import NCBITaxa
from os import path
from natsort import natsorted

# to be able to report line number in error messages
import inspect
frame = inspect.currentframe()

# debug
b_test_load_h_taxid_acc = False # ok 2022 01 21
b_test_read_ncbi_taxonomy_retain_acc_under_taxid = False # ok 2022 01 21

prog_tag = '[' + os.path.basename(__file__) + ']'

# list of interesting taxid (fathers)
taxidlist_f = ''
taxidlist = []

# store key taxid, value accesssion number for all records in krona tab file
h_taxid_acc = {}

searched_taxid = -1
krona_taxid_acc_f = ''
krona_tab_dir = ''

# taxid found under the taxid searched for
tax_in = []

# directory where are stored taxid.tsv files with accession numbers found under taxid in megablast result
# acc_out_dir_in = ''
# acc_out_dir_out = ''

# boolean to know if we dowload ncbi taxonomy file in current env
b_load_ncbi_tax_f = False
b_test_all = False
b_test = False
b_acc_in_f = False
b_acc_out_f = False

b_verbose = False

min_nr_reads_by_accnr = 1

parser = argparse.ArgumentParser()
parser.add_argument("-t", "--taxid", dest='taxidlist_f',
                    help="txt file with list of taxid to keep nodes/acc_nr we want to select (in) or remove (out) in taxid_acc_tabular_f tabular file. (One taxid per line)",
                    metavar="FILE")
parser.add_argument("-r", "--taxid_acc_tabular_f", dest='taxid_acc_tabular_f',
                    help="taxid acc tabular file (output of MEGABLAST_TAB_get_taxid_acc.py ran on megablast 25 column tabular file)",
                    metavar="FILE")
parser.add_argument("-i", "--acc_in_f", dest='acc_in_f',
                    help="[optional if --acc_out_f provided] Output text file with accession numbers from krona_taxid_acc_f found under taxid in ncbi taxonomy tree",
                    metavar="FILE")
parser.add_argument("-o", "--acc_out_f", dest='acc_out_f',
                    help="[optional if --acc_in_f provided] Output text file with accession numbers from krona_taxid_acc_f NOT found under taxid in ncbi taxonomy tree",
                    metavar="FILE")
parser.add_argument("-m", "--min_number_off_reads_by_acc_nr", dest='min_nr_reads_by_accnr',
                    help="[Optional] minimal number of reads matching an accession number to take it into account (default:1)",
                    metavar="INT")
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
parser.set_defaults(min_nr_reads_by_accnr=1)
parser.set_defaults(b_verbose=False)

# get absolute path in case of files
args = parser.parse_args()

# -------------------------------------------
# check arguments
b_test_all = args.b_test_all

if b_test_all:
    b_test_load_h_taxid_acc = True
    b_test_read_ncbi_taxonomy_retain_acc_under_taxid = True
    b_test = True
    b_acc_in_f = True
    b_acc_out_f = True
else:
    b_test = (b_test_load_h_taxid_acc or
              b_test_read_ncbi_taxonomy_retain_acc_under_taxid)

if ((not b_test)and
    ((len(sys.argv) < 9) or (len(sys.argv) > 15))):
    print("\n".join(["To use this scripts, run:",
                                "conda activate MEGABLAST_TAB_select_acc_under_taxids",
                                "./MEGABLAST_TAB_select_acc_under_taxids.py --test_all --load_ncbi_tax_f",
                                " ",
                                "Then you won't need --test_all --load_ncbi_tax_f options\n\n",
                     "Example: "+ ' '.join(['./MEGABLAST_TAB_select_acc_under_taxids.py',
                                                  '-t taxid_wanted_list.txt',
                                                  '-r megablast_out_f_taxid_acc.tsv',
                                                  '-i megablast_out_f_acc_in_taxid.tsv',
                                                  '-o megablast_out_f_acc_out_taxid.tsv']),"\n\n" ]))
    parser.print_help()
    print(prog_tag + "[Error] we found "+str(len(sys.argv)) +
          " arguments, exit line "+str(frame.f_lineno))
    sys.exit(0)

# print('args:', args)
# if(not b_test):
if args.taxid_acc_tabular_f is not None:
    taxid_acc_tabular_f = os.path.abspath(args.taxid_acc_tabular_f)
elif(not b_test):
    sys.exit("[Error] You must provide taxid_acc_tabular_f")
if args.ncbi_tax_f is not None:
    ncbi_tax_f = os.path.abspath(args.ncbi_tax_f)
else:
    # ncbi_tax_f = "/nfs/data/db/ete3/taxa.sqlite"
    ncbi_tax_f = os.path.expanduser("~/.etetoolkit/taxa.sqlite")
if args.acc_in_f is not None:
    acc_in_f = os.path.abspath(args.acc_in_f)
    b_acc_in_f = True
if args.acc_out_f is not None:
    acc_out_f = os.path.abspath(args.acc_out_f)
    b_acc_out_f = True
if args.taxidlist_f is not None:
    taxidlist_f = os.path.abspath(args.taxidlist_f)
    taxidlist_f_handle = open(taxidlist_f, "r")
    for line in taxidlist_f_handle:
        line = line.rstrip()
        taxidlist.append(line)
elif(not b_test):
    sys.exit("-taxidlist_f <taxid_file>n must be provided\n")
if min_nr_reads_by_accnr is not None:
    min_nr_reads_by_accnr = int(args.min_nr_reads_by_accnr)

if(not b_test):
    if (not b_acc_in_f) and (not b_acc_out_f):
        sys.exit(prog_tag + "[Error] You must provide either --acc_in_f <file> or -acc_out_f <file>, none provided currently")

# --------------------------------------------------------------------------
# load krona tab file and record hash table with key:taxid val:accession_number
# --------------------------------------------------------------------------
def load_h_taxid_acc(taxid_acc_tabular_f):

    if not path.exists(taxid_acc_tabular_f):
        sys.exit("Error " + taxid_acc_tabular_f +
                 " file does not exist, line "+ str(sys._getframe().f_lineno) )

    cmd = "cut -f 1,2 "+taxid_acc_tabular_f+" | sort | uniq "
    # stream = os.popen(cmd).read()
    # print(stream)
    # sys.exit()
    for line in os.popen(cmd).readlines():
        # print("line:"+line)
        k, v = line.split()
        # print("v:"+v)
        if k in h_taxid_acc:
            if v not in h_taxid_acc[ k ]:
                h_taxid_acc[ k ].append(v)
        else:
            h_taxid_acc[ k ] = [ v ]


# test load_h_taxid_acc procedure
# display h_taxid_acc, then exit
if b_test_load_h_taxid_acc:
    taxid_acc_tabular_f = 'megablast_out_f_taxid_acc.tsv'
    print("START b_test_load_h_taxid_acc")
    print("loading "+taxid_acc_tabular_f+" file")
    load_h_taxid_acc(taxid_acc_tabular_f)
    for k, v in h_taxid_acc.items():
        print(k, v)
    print("END b_test_load_h_taxid_acc")
    if not b_test_read_ncbi_taxonomy_retain_acc_under_taxid:
        sys.exit()
# --------------------------------------------------------------------------

# --------------------------------------------------------------------------
# Read ncbi_tax_f that represent taxid tree only from node taxid
# retain accession numbers under this node that are found in h_taxid_acc
# --------------------------------------------------------------------------
def read_ncbi_taxonomy_retain_acc_under_taxid(taxidlist,  # list of taxids under which we search for accession number of krona tab
                                              h_taxid_acc,# hash table storing key:taxid val:acc_number in krona tab file
                                              ncbi_tax_f, # ncbi taxonomy file, browsed to find taxid, then taxid/acc under
                                              krona_taxid_acc_f, # megablast file reduced to acc and taxid only
                                              acc_in_f,   # outfile stores acc number of h_taxid_acc found
                                              acc_out_f   # outfile stores acc number of h_taxid_acc not found
):
    if not path.exists(ncbi_tax_f):
        warnings.warn(prog_tag + "[Warn] "+ ncbi_tax_f+
                 " file does not exist, line "+ str(sys._getframe().f_lineno) )
    if not path.exists(krona_taxid_acc_f):
        sys.exit(prog_tag + "Error ", krona_taxid_acc_f,
                 " file does not exist, line ", str(sys._getframe().f_lineno) )

    print(prog_tag + " min_nr_reads_by_accnr:"+str(min_nr_reads_by_accnr))
    print(prog_tag + " List of given taxid"+str(taxidlist))
    ### Output:
    if b_acc_in_f and acc_in_f:
        if path.exists(acc_in_f):
            os.remove(acc_in_f)
        acc_in_f_handle = open(acc_in_f,"a")

    if b_acc_out_f and acc_out_f:
        if path.exists(acc_out_f):
            os.remove(acc_out_f)
        acc_out_f_handle = open(acc_out_f,"a")

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
        list_tax = ncbi.get_descendant_taxa(tax, intermediate_nodes=True)
        list_tax.sort()
        # print("Length of tax extracted:"+str(len(list_tax)))
        for taxl in list_tax:
            all_tax_extract.add(str(taxl))
    # # verif ok
    # print("all_tax_extract:")
    # print(', '.join(natsorted(all_tax_extract)))
    # sys.exit("all_tax_extract check end")

    # read megablast results with on each line one taxid and one accession number
    krona_taxid_acc_f_handle = open(krona_taxid_acc_f, "r")
    # print(krona_taxid_acc_f, " opened, line ", str(sys._getframe().f_lineno) )

    # get all tax ids of megablast result and all acc
    all_megablast_tax = set()

    h_megablast_tax = {} # record valid acc (number of occ sufficient) foreach valid tax
    h_megablast_acc = {} # count occ for each acc nr
    for line in krona_taxid_acc_f_handle:
        line = line.rstrip()
        # get megablast res taxid
        try:
            research_tax, acc = line.split()

            b_valid_acc = False

            if acc not in h_megablast_acc:
                h_megablast_acc[acc] = 1

                if  h_megablast_acc[acc] == min_nr_reads_by_accnr:
                    # print("num acc:"+acc+" (tax:"+research_tax+"), "+ str(h_megablast_acc[acc]) + ": RECORDED >= "+str(min_nr_reads_by_accnr))
                    all_megablast_tax.add(research_tax)
                    b_valid_acc = True
            elif h_megablast_acc[acc] < min_nr_reads_by_accnr:
                h_megablast_acc[acc] = h_megablast_acc[acc] + 1
                if  h_megablast_acc[acc] == min_nr_reads_by_accnr:
                    # print("num acc:"+acc+" (tax:"+research_tax+"), "+ str(h_megablast_acc[acc]) + ": RECORDED >= "+str(min_nr_reads_by_accnr))
                    all_megablast_tax.add(research_tax)
                    b_valid_acc = True
            else:
                h_megablast_acc[ acc ] = h_megablast_acc[ acc ] + 1

            if b_valid_acc:
                if research_tax not in h_megablast_tax:
                    h_megablast_tax[ research_tax ] = [acc]
                else:
                    h_megablast_tax[ research_tax ].append(acc)


        # sometimes triggered when taxid related to acc number is missing
        # you can also have an error message on first line to tail krona tax db must be
        # updated because of missing acc
        except ValueError:
            # print("No taxid found for an acc in line ",line)
            sys.exit("No taxid found for an acc in line ",line)

    print(prog_tag + " Number of different taxid in krona_taxid_acc_f results:"+ str(len(all_megablast_tax)))
    # # verif ok
    # print("all_megablast_tax:")
    # print(', '.join(all_megablast_tax))
    # sys.exit("all_megablast_tax check end")

    krona_taxid_acc_f_handle.close()
    
    # intersection of the two lists to get tax in megablast results that are in the
    # phylogeny of taxids provided by user
    tax_in_set = all_tax_extract.intersection(all_megablast_tax)
    tax_in = natsorted(list(tax_in_set))

    # remove all ncbi tax ids found to be under the one wanted by user
    # to the list of all megablast taxids
    tax_out_set = all_megablast_tax.difference(tax_in_set)
    tax_out = natsorted(list(tax_out_set))

    # # verif ok
    # print("tax_in:")
    # print(', '.join(tax_in))
    # sys.exit("tax_in check end")

    # write output file of acc numbers included in taxid provided by user
    if b_acc_in_f:
        for tax in tax_in:

            # write only recorded acc for current taxid (only those are are >= min_nr_reads_by_accnr)
            acc_in_f_handle.write("\n".join(h_megablast_tax[ tax ]))
            acc_in_f_handle.write("\n")
            if b_verbose:
                print(prog_tag + " record acc in :"+",".join(h_megablast_tax[tax])+" from taxid:"+tax)

        acc_in_f_handle.close()
        print(prog_tag + ' '+ acc_in_f+" file created")

    # write output file of acc numbers NOT included in taxid provided by user
    if b_acc_out_f:
        for tax in tax_out:

            # write only recorded acc for current taxid (only those are are >= min_nr_reads_by_accnr)
            acc_out_f_handle.write("\n".join(h_megablast_tax[ tax ]))
            acc_out_f_handle.write("\n")
            if b_verbose:
                print(prog_tag + " record acc out:"+",".join(h_megablast_tax[tax])+" from taxid:"+tax)

        acc_out_f_handle.close()
        print(prog_tag + ' '+ acc_out_f+" file created")
        
if b_test_read_ncbi_taxonomy_retain_acc_under_taxid:
    print("START b_test_read_ncbi_taxonomy_retain_acc_under_taxid")
    ncbi_tax_f = os.path.expanduser("~/.etetoolkit/taxa.sqlite")
    acc_in_f = "megablast_out_f_acc_in_taxid.tsv"
    acc_out_f = "megablast_out_f_acc_out_taxid.tsv"
#     taxidlist = ['10295', '10293'] # bovine herpes virus, alphaherpesvirinae
#     taxidlist = ['10295'] # bovine herpes virus ok 2022 01 27
    taxidlist = ['10239'] # virus ok 2022 01 27
    # min_nr_reads_by_accnr = 1
    krona_taxid_acc_f = 'megablast_out_f_taxid_acc.tsv'

    print("load krona_taxid_acc_f:"+krona_taxid_acc_f)
    load_h_taxid_acc(krona_taxid_acc_f)
    # for k, v in h_taxid_acc.items():
    #    print(k, v)
    print("load krona_taxid_acc_f: done")

    read_ncbi_taxonomy_retain_acc_under_taxid(taxidlist,
                                              h_taxid_acc,
                                              ncbi_tax_f,
                                              krona_taxid_acc_f,
                                              acc_in_f,
                                              acc_out_f)
    print("END b_test_read_ncbi_taxonomy_retain_acc_under_taxid")
    sys.exit()
    
# --------------------------------------------------------------------------

# --------------------------------------------------------------------------
# MAIN
# --------------------------------------------------------------------------
##### MAIN
def __main__():
    # load taxid_acc file
    load_h_taxid_acc(taxid_acc_tabular_f)
    # check in ncbi taxonomy which acc number are in and out of given taxid
    read_ncbi_taxonomy_retain_acc_under_taxid(taxidlist,
                                              h_taxid_acc,
                                              ncbi_tax_f,
                                              taxid_acc_tabular_f,
                                              acc_in_f,
                                              acc_out_f)
    # --------------------------------------------------------------------------
#### MAIN END
if __name__ == "__main__": __main__()
  
