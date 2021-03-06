#! /usr/bin/env python

####################
###Get the options
import argparse
parser = argparse.ArgumentParser(description='Sort amplicon sequences tagged on each end by tag combination')
parser.add_argument("-fq", required=True, help='Input fastq with amplicon sequences')
parser.add_argument("-p",  required=True, help='Input text file with primer name and forward and reverse sequences [Format: Name\tForwardSeq\tReverSeq]')
parser.add_argument("-t",  required=True, help='Input text file with tag names and sequences [Format: TagSeq\tTagName]')
parser.add_argument("--keepPrimersSeq",  help='Use this parameter if you want to keep the primer sequences from the amplicon instead of trimming it [default not set]', action="store_true")

args = parser.parse_args()

####################

from modules_sort import *

######################
##Initialize variables
filename= args.fq 
primers= args.p
tags= args.t
keepPrimersSeq=args.keepPrimersSeq

CountErrors=0

#Initialize dict
AMBIG={'A' : "A", 'B' : "[CGT]", 'C' : "C", 'D' : "[AGT]", 'G' : "G", 'H' : "[ACT]", 'K' : "[GT]", 'M' : "[AC]", 'N' : "[ACGT]", 'R' : "[AG]", 'S' : "[CG]", 'T' : "T", 'V' : "[ACG]", 'W' : "[AT]", 'Y' : "[CT]"}
TAGS={} ## All the tags used. The keys are the name of the tag, and the values are [seq, RC(seq)]  #RC is ReverseComplement
PRIMERS={}
HAP={}
##################################
### Main program
##################################

### Read tags [Format:  TagSeq\tTagName]
TAGS=readTags(tags, TAGS)
### Read primers [Format:  PrimerSetName\tForwardSeq\tReverSeq]
PRIMERS=readPrimers(primers, PRIMERS, AMBIG)

### Sort the sequences into tag combinatios and collapse them
file = open(filename)
line= file.readline()    ### header line. 
while line:
	line= file.readline()  ### seq line. 
	line=line.rstrip()
	## Find primer and tags. RC the between if reverse. If it does not exist in the list (seq err or Ns or whatever) set a flag called Error
	Info= GetPiecesInfo(line, PRIMERS, TAGS, keepPrimersSeq)
	if len(Info)==1: # If there's a seq error
		line= file.readline()  ## "+" line. Ignore
		line= file.readline() ## Qual line. Ignore
		line= file.readline() # header line. 
		CountErrors+=1
	else:
		HAP=FillHAP(HAP, Info[0], Info[1], Info[2],Info[3])
		line= file.readline()  ## "+" line. Ignore
		line= file.readline() ## Qual line. Ignore
		line= file.readline() # header line. 

file.close() ## close input hander

## Go through the dictionary and print the entries to the proper output file
PrintSortedCollapsedCountedSeqs(HAP)

## And print a summary counts file
PrintSummaryFile(HAP)

## Report how many seqs had errors in the primer or in the tags
print "Number of erroneous sequences (with errors in the sequence of primer or tags, or no barcode amplified): "+str(CountErrors)

