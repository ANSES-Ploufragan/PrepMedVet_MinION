# -*- coding: utf-8 -*-
### Libraries to import:
import argparse, os, sys, re
from os import path

### GET md5 contained in md5sum file
def Readmd5file(md5file):
  for l in open(md5file,'r').readlines():
    md5sum = l.rstrip().split("\t")[0]
  return md5sum
  
##### MAIN
def __main__():
  ### Script options:
  parser = argparse.ArgumentParser(description='''Update database from NCBI, check md5sum and download if different.''',
    epilog="""This script need few options, use -h to see it.""")
  parser.add_argument ('-db', '-database', dest='db', help='Choose database, available now: krona, krona_accession.')
  parser.add_argument ('-di', '-directory', dest='dire', help='Directory to download.')
  ### Get script options:
  options = parser.parse_args()
  db = options.db
  di = options.dire

  ### Check options:
  if len(sys.argv)==1 or len(sys.argv)<5 or len(sys.argv)>5:
    parser.print_help()
    sys.exit(1)

  ### Check output dir
  if path.exists(di) == False or path.isdir(di) == False:
    os.mkdir(di)
  
  ### Change workdir
  current_dir = os.getcwd()
  os.chdir(di)

  if db == "krona":
    seq_file = "taxdump.tar.gz"
    md5file = seq_file+".md5"
    new_md5file = md5file+".WGET"
    seq_md5file = md5file+".SEQ"
    ### NCBI conf
    https = "https://ftp.ncbi.nih.gov/pub/taxonomy/"
    ### md5 file already exist
    if path.isfile(md5file) == True:
      print("md5 file "+md5file+" already exist")  
      print("Download this file: "+md5file+" into "+new_md5file)
      os.system("wget -c "+https+md5file+" -O "+new_md5file)
      md5sum_origin = Readmd5file(md5file)
      print(md5sum_origin)
      md5sum_new = Readmd5file(new_md5file)
      print(md5sum_new)
      if md5sum_origin == md5sum_new:
        print("md5 file "+md5file+" is the same.")
        os.remove(new_md5file)
      else:
        print("md5 file "+md5file+" is not the same, need to re-download taxdump file.") 
        os.remove(md5file)
        os.system("mv "+new_md5file+" "+md5file)
    ### new index
    else:
      print("md5 file "+md5file+" doesn't exist")
      print("Download this file: "+md5file)
      os.system("wget -c "+https+md5file)
    ### No seq file downloaded
    if path.isfile(seq_file) == False:
      print("Download this file: "+seq_file)
      os.system("wget -c "+https+seq_file) 
    ### Checking md5
    md5sum_origin = Readmd5file(md5file)
    os.system("md5sum "+seq_file+" > "+seq_md5file)
    md5sum_seq = Readmd5file(seq_md5file)
    print("Check md5")
    while md5sum_seq != md5sum_origin:
      os.remove(seq_file)
      os.system("wget -c "+https+seq_file)
      os.system("md5sum "+seq_file+" > "+seq_md5file)
      md5sum_seq = Readmd5file(seq_md5file)
    if path.isfile(seq_md5file):
      os.remove(seq_md5file)
    ### Untar and unzip archive
    print("tar -xvf "+seq_file)
    os.system("tar -xvf "+seq_file) 
    print("Ok for taxdump file: "+seq_file)
  elif db == "krona_accession":
    list_accession = ["dead_nucl", "dead_prot", "dead_wgs", "nucl_gb", "nucl_wgs", "prot"]
    for f in list_accession:
      gunzip_file = f+".accession2taxid"
      seq_file = f+".accession2taxid.gz"
      md5file = seq_file+".md5"
      new_md5file = md5file+".WGET"
      seq_md5file = md5file+".SEQ"
      ### NCBI conf
      https = "https://ftp.ncbi.nih.gov/pub/taxonomy/accession2taxid/"
      ### md5 file already exist
      if path.isfile(md5file) == True:
        print("md5 file "+md5file+" already exist")  
        print("Download this file: "+md5file+" into "+new_md5file)
        os.system("wget -c "+https+md5file+" -O "+new_md5file)
        md5sum_origin = Readmd5file(md5file)
        print(md5sum_origin)
        md5sum_new = Readmd5file(new_md5file)
        print(md5sum_new)
        if md5sum_origin == md5sum_new:
          print("md5 file "+md5file+" is the same.")
          os.remove(new_md5file)
        else:
          print("md5 file "+md5file+" is not the same, need to re-download taxdump file.") 
          os.remove(md5file)
          os.system("mv "+new_md5file+" "+md5file)
      ### new index
      else:
        print("md5 file "+md5file+" doesn't exist")
        print("Download this file: "+md5file)
        os.system("wget -c "+https+md5file)
      ### No seq file downloaded
      if path.isfile(seq_file) == False:
        print("Download this file: "+seq_file)
        os.system("wget -c "+https+seq_file) 
      ### Checking md5
      md5sum_origin = Readmd5file(md5file)
      os.system("md5sum "+seq_file+" > "+seq_md5file)
      md5sum_seq = Readmd5file(seq_md5file)
      print("Check md5")
      while md5sum_seq != md5sum_origin:
        os.remove(seq_file)
        os.system("wget -c "+https+seq_file)
        os.system("md5sum "+seq_file+" > "+seq_md5file)
        md5sum_seq = Readmd5file(seq_md5file)
      if path.isfile(seq_md5file):
        os.remove(seq_md5file)
      ### Untar and unzip archive
      print("gunzip -k "+seq_file)
      os.system("gunzip -k "+seq_file) 
      print("Ok for this file: "+seq_file)

#### MAIN END
if __name__ == "__main__": __main__()
