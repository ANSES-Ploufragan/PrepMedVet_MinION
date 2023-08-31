#!/usr/bin/env python3
import argparse, os, sys, json
from os import path
from Bio import Entrez
Entrez.email = 'fabrice.touzain@anses.fr'

# to be able to report line number in error messages
import inspect
frame = inspect.currentframe()

# debug
b_test = False      # ok 2023 08 25

prog_tag = '[' + os.path.basename(__file__) + ']'

# variables
b_test                   = False
b_test_load_taxids       = False # ok 2023 08 31
b_test_accession2taxid   = False # ok 2023 08 31
b_test_accessions2taxids = True # 

b_acc_in_f        = False
acc_in_f          = None
taxid_acc_out_f   = None
b_verbose         = False

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--acc_in_f", dest='acc_in_f',
                    help="acc_number list in tsv (tabular separated at each line)",
                    metavar="FILE")
parser.add_argument("-o", "--taxid_acc_out_f", dest='taxid_acc_out_f',
                    help="taxid acc_number list in tsv (tabular separated at each line)",
                    metavar="FILE")
parser.add_argument("-z", "--test", dest='b_test',
                    help="[Optional] run all tests",
                    action='store_true')
parser.set_defaults(b_verbose=False)

args = parser.parse_args()

# -------------------------------------------
# check arguments
b_test = args.b_test

if ((not b_test)and
    (not b_test_load_taxids)and
    (not b_test_accession2taxid)and
    (not b_test_accessions2taxids)and
    ((len(sys.argv) < 2) or (len(sys.argv) > 2))):
    print("\n".join([
        "Aim: find taxids from accession numbers.",
        "Example:",
        ' '.join([f"./{prog_tag}",
                  '-i accnr_list.tsv',
                  '-o taxid_accnr_list.tsv']) ]))
    parser.print_help()
    print(prog_tag + "[Error] we found "+str(len(sys.argv)) +
          " arguments, exit line "+str(frame.f_lineno))
    sys.exit(0)

if b_test:
    acc_in_f = "../taxid_lists/host_complete_genomes_accnr.txt"
    taxid_acc_out_f = "../taxid_lists/host_complete_genomes_accnr_taxid.tsv"
    b_test_load_taxids       = True
    b_test_accession2taxid   = True
    b_test_accessions2taxids = True

b_one_test = (b_test or b_test_load_taxids or b_test_accession2taxid or b_test_accessions2taxids)
print(f"b_one_test:{b_one_test}")

# print('args:', args)
# if(not b_test):
if args.acc_in_f is not None:
    acc_in_f = os.path.abspath(args.acc_in_f)
    b_acc_in_f = True
elif(not b_one_test):
    sys.exit("[Error] You must provide --acc_in_f")
if args.taxid_acc_out_f is not None:
    taxid_acc_out_f = os.path.abspath(args.taxid_acc_out_f)
    b_out_f = True
elif(not b_one_test):
    sys.exit("[Error] You must provide taxid_acc_out_f")

if args.b_verbose is not None:
    b_verbose = int(args.b_verbose)

if(not b_one_test):
    if (not b_acc_in_f) or (not b_out_f):
        sys.exit(prog_tag + "[Error] You must provide --acc_in_f <file> and --taxid_acc_out_f <file>")

# --------------------------------------------------------------------------
# Function: load taxid acc list, return accession number list
# --------------------------------------------------------------------------
def load_taxids(acc_tabular_f):

    if not path.exists(acc_tabular_f):
        sys.exit("Error " + acc_tabular_f +
                 " file does not exist, line "+ str(sys._getframe().f_lineno) )

    accnrlist_l = [] # list of searched accession numbers
    cmd = "cat "+acc_tabular_f+" | sort | uniq "

    for line in os.popen(cmd).readlines():
        if line.rstrip() != "":
            a = line.rstrip() # .split()
            accnrlist_l.append(a)
            # print(f"last item added to accnrlist_l:{accnrlist_l[-1]}, line {str(sys._getframe().f_lineno)}")
    # print(f"accnrlist_l:{accnrlist_l}")
    return accnrlist_l

if b_test_load_taxids:
    print(f"{prog_tag} [TEST load_taxids] START")
    accnrlist = load_taxids(acc_in_f)
    print(f"accnrlist:{accnrlist}")
    print(f"{prog_tag} [TEST load_taxids] END")
# --------------------------------------------------------------------------

# --------------------------------------------------------------------------
# Function: deduce 1 taxid from 1 accession number
# --------------------------------------------------------------------------
def accession2taxid(acc: str, db="nucleotide") -> str:
    handle = Entrez.esearch(db=db, term=acc)
    record = Entrez.read(handle)
    gi = record["IdList"][0]
    handle = Entrez.esummary(db=db, id=gi, retmode="json")
    result = json.load(handle)["result"]
    taxid = result[gi]["taxid"]
    return str(taxid)

if b_test_accession2taxid:
    print(f"{prog_tag} [TEST accession2taxid] START")
    taxid = 'GCA_000005845.2'
    accnr = accession2taxid(taxid)
    print(f"accnr:{accnr} taxid:{taxid}")
    print(f"{prog_tag} [TEST accession2taxid] END")
# --------------------------------------------------------------------------

# --------------------------------------------------------------------------
# Function: deduce taxidS from an accession numberS (many IDs)
# --------------------------------------------------------------------------
def accessions2taxids(acc: list, db="nucleotide") -> list:

    print(f"acc:{acc} line {str(frame.f_lineno)}")
    # first we do a post with the list of ids and we get the cookie (under the form of a web environnement) and a query id :
    id_str = ','.join(acc)
    try:
        handle = Entrez.epost(db = 'nucleotide', id = acc)
    except IOError:
        sys.exit(f"{prog_tag} [Error] Network error for Entrez.epost line {str(frame.f_lineno)}")

    print(f"id:{id_str} line {str(frame.f_lineno)}")
    result = Entrez.read(handle)
    webEnv = result['WebEnv']
    queryKey = result['QueryKey']
    gi = result["IdList"][0]
        
    # then, we reuse this env to ask for the related entries :
    handle = Entrez.efetch(db = 'genome', webenv = webEnv, query_key = queryKey,
                           rettype = 'taxid', retmode = 'json')
    result = Entrez.read(handle)
    handle.close()
    print(f"results:{result}")
    return result

if b_test_accessions2taxids:
    print(f"{prog_tag} [TEST accessions2taxids] START")
    taxids = ['GCA_000005845.2','GCF_000091125.1']
    accnrs = accessions2taxids(taxids)
    if len(accnrs) != len(taxids):
        sys.exit(f"{prog_tag} [ERROR] number of taxids returned by accessions2taxids diff from number of accnrs provided, line {str(frame.f_lineno)}")
    for i in range(taxids):
        print(f"accnr:{accnrs[i]} taxid:{taxids[i]}")
    print(f"{prog_tag} [TEST accessions2taxids] END")
# --------------------------------------------------------------------------


accnrs = load_taxids(acc_in_f)
taxids = accessions2taxids(accnrs, db="assembly")