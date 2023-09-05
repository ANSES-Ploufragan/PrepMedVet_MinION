#!/usr/bin/env python3
import argparse, os, sys, json, time, warnings
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
b_test_accessions2taxids = False # ko epost seems to need gi, need efetch but unclear, maybe incompatible with assemblies acc nr
b_test_accessions2taxids_1by1 = False  # ok 2023 09 05, handle missing acc nr in ncbi (suppressed)

b_acc_in_f        = False
acc_in_f          = None
taxid_acc_out_f   = None
b_verbose         = False
miss_acc_out_f    = None # list of accession numbers suppressed in ncbi and to get manually

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--acc_in_f", dest='acc_in_f',
                    help="acc_number list in tsv (tabular separated at each line)",
                    metavar="FILE")
parser.add_argument("-o", "--taxid_acc_out_f", dest='taxid_acc_out_f',
                    help="taxid acc_number list in tsv (tabular separated at each line)",
                    metavar="FILE")
parser.add_argument("-d","--miss_acc_out_f", dest='miss_acc_out_f',
                    help="acc number NOW missing in ncbi: list",
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
    (not b_test_accessions2taxids_1by1)and
    ((len(sys.argv) < 2) or (len(sys.argv) > 8))):
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
    b_test_accessions2taxids_1by1 = True

b_one_test = (b_test or b_test_load_taxids or b_test_accession2taxid or b_test_accessions2taxids or b_test_accessions2taxids_1by1)
# print(f"b_one_test:{b_one_test}")

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
if args.miss_acc_out_f is not None:
    miss_acc_out_f = os.path.abspath(args.miss_acc_out_f)
    record_del = open(miss_acc_out_f, 'w')
    b_miss_f = True
elif(not b_one_test):
    sys.exit("[Error] You must provide miss_acc_out_f for cases when acc nr has been suppressed in ncbi")

if args.b_verbose is not None:
    b_verbose = int(args.b_verbose)

if b_one_test:
    miss_acc_out_f = "../taxid_lists/host_complete_genomes_missing_accnr.txt"
    miss_acc_out_f = os.path.abspath(miss_acc_out_f)
    record_del = open(miss_acc_out_f, 'w')
else:
    if (not b_acc_in_f) or (not b_out_f) or (not b_miss_f):
        sys.exit(prog_tag + "[Error] You must provide --acc_in_f <file> and --taxid_acc_out_f <file> and --miss_acc_out_f <file>")

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
    if(not b_test_accession2taxid)and(not b_test_accessions2taxids)and(not b_test_accessions2taxids_1by1):
        sys.exit(0)
# --------------------------------------------------------------------------

# --------------------------------------------------------------------------
# Function: deduce 1 taxid from 1 accession number
# --------------------------------------------------------------------------
def accession2taxid(acc: str, db="nucleotide") -> str:
    handle = Entrez.esearch(db=db, term=acc)
    record = Entrez.read(handle)
    try:
        gi = record["IdList"][0]
    except IndexError as ie:
        acc_ssnr = acc.split('.')[0]
        print(f"{prog_tag} {acc} record probably suppressed, try without version number {acc_ssnr}")
        handle.close()
        handle = Entrez.esearch(db=db, term=acc_ssnr)
        record = Entrez.read(handle)
        try:
            gi = record["IdList"][0]
        except IndexError as err:
            warnings.warn("{prog_tag} {acc_ssnr} does not exist anymore in ncbi, check this accnr manually using {miss_acc_out_f} file")
            record_del.write(f"{acc}\n")
            return ''

    handle = Entrez.esummary(db=db, id=gi, retmode="json")
    result = json.load(handle)["result"]
    taxid = result[gi]["taxid"]
    handle.close()
    return taxid

if b_test_accession2taxid:
    print(f"{prog_tag} [TEST accession2taxid] START")
    accnr = 'GCF_000001735.4'
    taxid = accession2taxid(accnr)
    print(f"accnr:{accnr} taxid:{taxid}")
    print(f"{prog_tag} [TEST accession2taxid] END")
    if(not b_test_accessions2taxids)and(not b_test_accessions2taxids_1by1):
        sys.exit(0)
# --------------------------------------------------------------------------

# --------------------------------------------------------------------------
# Function: deduce taxidS from an accession numberS (many IDs)
# --------------------------------------------------------------------------
def accessions2taxids(acc: list, db="Taxonomy") -> list:

    handle = Entrez.esearch(db="nucleotide", term=acc)
    record = Entrez.read(handle)
    gi = record["IdList"][0]

    handle = Entrez.efetch(db=db, id=gi, retmode='xml')
    record = Entrez.read(handle)
    print(f"record:{record[0].keys()}")
    # taxids = record["TSeq_taxid"]
    handle.close()
    return taxids

    """
    # post avec la liste des ids, on récupère en retour le cookie (environnement web) 
    # et un id de query :
    handle = Entrez.epost(db='nuccore', id=','.join(acc), idtype='acc')
    result = Entrez.read(handle)
    webEnv = result['WebEnv']
    queryKey = result['QueryKey']
        

    # puis, on réutilise cet environnement pour demander les entrées correspondantes :
    handle = Entrez.efetch(db = 'nuccore', webenv = webEnv, query_key = queryKey,
                           rettype = 'fasta', retmod = 'xml')
    result = Entrez.read(handle)
    handle.close()
    print(f"result:{result}")
    """
    
    """
    curr_first_index = 0 
    curr_last_index = min(len(acc),200)

    taxids_a2t = []
    while curr_first_index <= len(acc):
        id_str = ','.join( acc[curr_first_index:curr_last_index] )
        taxids_a2t.append( accession2taxid(id_str) )
        curr_first_index += 200 
        curr_last_index += 200 
        curr_last_index = min(curr_last_index, len(acc))

    print(f"results:{','.join(str(taxids_a2t))}")
    """

    # return taxids_a2t

if b_test_accessions2taxids:
    print(f"{prog_tag} [TEST accessions2taxids] START")
    accnrs = ['GCA_000005845.2','GCF_000001735.4']
    taxids = accessions2taxids(accnrs)
    if len(accnrs) != len(taxids):
        sys.exit(f"{prog_tag} [ERROR] number of taxids returned by accessions2taxids diff from number of accnrs provided, line {str(frame.f_lineno)}")
    for i in range(taxids):
        print(f"accnr:{accnrs[i]} taxid:{taxids[i]}")
    print(f"{prog_tag} [TEST accessions2taxids] END")
    if not b_test_accessions2taxids_1by1:
        sys.exit(0)
# --------------------------------------------------------------------------

# --------------------------------------------------------------------------
# Function: deduce n taxid from n accession number, but 1 by 1 call
# --------------------------------------------------------------------------
def accessions2taxids_1by1(acc: list) -> list:
    taxids = []
    for a in acc:
        taxids.append(accession2taxid(str(a)))
        print(f"acc:{a}\ttaxid:{taxids[-1]}")
        # needed because ncbi for not post method accept less than 3 request by sec
        # here: 2 request by sec
        time.sleep(0.5)
    return taxids

if b_test_accessions2taxids_1by1:
    print(f"{prog_tag} [TEST accessions2taxids_1by1] START")
    # GCF_000002295.2 triggers list index out of range for record["IdList"][0]
    # GCF_000002295.1 triggers list index out of range for record["IdList"][0]
    # GCA_000002295.1 triggers list index out of range for record["IdList"][0]
    accnrs = ['GCA_000005845.2','GCF_000001735.4','GCF_000002295.2']
    taxids = accessions2taxids_1by1(accnrs)
    print(f"accnr:{accnrs} taxid:{taxids}")
    print(f"{prog_tag} [TEST accessions2taxids_1by1] END")
    sys.exit(0)
# --------------------------------------------------------------------------

accnrs = load_taxids(acc_in_f)
taxids = accessions2taxids_1by1(accnrs)
if b_out_f:
    with open(taxid_acc_out_f, "w") as record_file:
        for a in range(len(accnrs)):
            record_file.write("%s %s\n" % (taxids[a], accnrs[a]))
    record_del.close()
    record_file.close()
    print(f"{prog_tag} {taxid_acc_out_f} file written")
    print(f"{prog_tag} {miss_acc_out_f} file written")
   