#!/usr/bin/env python
# -*- coding: utf-8 -*-
###
# From a megablast file of results (tabular 25 columns) and taxid(s) user is interested in,
# provide 1 file with 2 columns: taxids acc
###

### Libraries to import:
# NOTE: Python 2.7 because needs krona env that MUST use 2.7 (last krona version load 2022 01 21)
# NOTE: to update krona tax in conda env, run:
# ktUpdateTaxonomy.sh
# ktUpdateTaxonomy.sh --accessions (this one NOT PROVIDED IN DOCUMENTATION)
import argparse, os, sys, warnings
# NEEDS to use krona conda environnement if access ktGetTaxIDFromAcc
from os import path

# to be able to report line number in error messages
import inspect
frame = inspect.currentframe()

# debug
b_test_creates_taxid_acc_f_from_megablast_res = False # ok 2022 01 21

prog_tag = '[' + os.path.basename(__file__) + ']'

krona_taxid_acc_f = ''
krona_tab_dir = ''

# taxid found under the taxid searched for
tax_in = []

# boolean to know if we dowload ncbi taxonomy file in current env
b_test_all = False
b_test = False

# min_nr_reads_by_accnr = 1

parser = argparse.ArgumentParser()
parser.add_argument("-r", "--megablast_tabular_f", dest='megablast_f',
                    help="megablast results tabular file (25 colums), including accession numbers in col 2",
                    metavar="FILE")
parser.add_argument("-o", "--tax_acc_out_f", dest='tax_acc_out_f',
                    help="Output text file with accession numbers from krona_taxid_acc_f NOT found under taxid in ncbi taxonomy tree",
                    metavar="FILE")
#parser.add_argument("-m", "--min_number_off_reads_by_acc_nr", dest='min_nr_reads_by_accnr',
#                    help="[Optional] minimal number of reads matching an accession number to take it into account (default:1)",
#                    metavar="INT")
parser.add_argument("-z", "--test_all", dest='b_test_all',
                    help="[Optional] run all tests",
                    action='store_true')
parser.set_defaults(b_load_ncbi_tax_f=False)
parser.set_defaults(b_test_all=False)
parser.set_defaults(min_nr_reads_by_accnr=1)

args = parser.parse_args()

# -------------------------------------------
# check arguments
b_test_all = args.b_test_all

if b_test_all:
    b_test_creates_taxid_acc_f_from_megablast_res = True
    b_test = True
else:
    b_test = b_test_creates_taxid_acc_f_from_megablast_res

if ((not b_test)and
    ((len(sys.argv) < 5) or (len(sys.argv) > 5))):
    print("\n".join(["To use this scripts, install first MEGABLAST_TAB_get_acc_under_taxid_in_out.yaml conda env. Then run:",
                                "conda activate MEGABLAST_TAB_get_taxid_acc",
                                "ktUpdateTaxonomy.sh",
                                "ktUpdateTaxonomy.sh --accessions",
                                "\n\n",
                     "Example: "+ ' '.join(['./MEGABLAST_TAB_get_taxid_acc.py',
                                                  '-r megablast_out_f_25clmn.tsv',
                                                  '-o megablast_out_f_taxid_acc.tsv']),"\n\n" ]))
    parser.print_help()
    print(prog_tag + "[Error] we found "+str(len(sys.argv)) +
          " arguments, exit line "+str(frame.f_lineno))
    sys.exit(0)

# print('args:', args)
if(not b_test):
    if args.megablast_f is not None:
        # get absolute path in case of files        
        megablast_f = os.path.abspath(args.megablast_f)
    else:
        sys.exit("[Error] You must provide megablast_f")
    if args.tax_acc_out_f is not None:
        tax_acc_out_f = os.path.abspath(args.tax_acc_out_f)
    # if min_nr_reads_by_accnr is not None:
    #     min_nr_reads_by_accnr = args.min_nr_reads_by_accnr

# ------------------------------------------------------------------------
# from a megablast tsv output file with 25 columns, return a file with only
# taxid acc
# output file name provided as parameter
# ------------------------------------------------------------------------
krona_taxid_acc_f = ''
def creates_taxid_acc_f_from_megablast_res(megablast_f, tax_acc_out_f):
    acc_col_nb_in_megablast_res = str(2)
    krona_taxdb_f = os.path.expanduser('~/miniconda3/envs/krona/opt/krona/taxonomy/') # krona['taxdb'] # "/nfs/data/db/tax_krona/"
    if not os.path.isfile(krona_taxdb_f + 'all.accession2taxid.sorted'):
        sys.exit(prog_tag + "[Error] missing "+krona_taxdb_f+" file, please run 'ktUpdateTaxonomy.sh --accessions' in your krona conda environment (and 'ktUpdateTaxonomy.sh' before if you have not done)")

    # conda: "../envs/krona.yaml"
    cmd = ' '.join(["cut -f", acc_col_nb_in_megablast_res, megablast_f,
                   '| ktGetTaxIDFromAcc -tax ',krona_taxdb_f,' -p ',
                   # '| uniq ', # remove many redundant lines # DO NOT USE because need exact number of each acc nr
                   '> ',tax_acc_out_f]) # return lines:taxid acc
    # print("cmd:"+cmd)
    os.system(cmd)
    print(prog_tag + ' ' + tax_acc_out_f + " file created")

# test creates_taxid_acc_f_from_megablast_res function
# display created file and header
if b_test_creates_taxid_acc_f_from_megablast_res:
    megablast_f = "megablast_out_f_25clmn.tsv"
    print(prog_tag + " START b_test_creates_taxid_acc_f_from_megablast_res")
    print(prog_tag + " loading "+megablast_f+" file")
    tax_acc_out_f = 'megablast_out_f_taxid_acc.tsv'
    creates_taxid_acc_f_from_megablast_res(megablast_f, tax_acc_out_f)
    if os.path.isfile(tax_acc_out_f):
        print(prog_tag + " " + tax_acc_out_f + " file created, start with:")
        cmd = "head " + tax_acc_out_f
        print(os.system(cmd))
    else:
        sys.exit(prog_tag + "[Error] creates_taxid_acc_f_from_megablast_res has not created file "+tax_acc_out_f)
    print("END b_test_creates_taxid_acc_f_from_megablast_res")
    sys.exit("Exit program after test")

# --------------------------------------------------------------------------

# --------------------------------------------------------------------------
# MAIN
# --------------------------------------------------------------------------
##### MAIN
def __main__():
    # creates taxid acc file from megablast result
    creates_taxid_acc_f_from_megablast_res(megablast_f, tax_acc_out_f)

#### MAIN END
if __name__ == "__main__": __main__()
  
