#!/usr/bin/env python

# ----------------------------------------------------------------------------
# Copyright (c) 2016--, mockrobiota development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------


import sys
import getopt


usage = '''usage: database-identifiers.py -i <source_fp>
                                          -o <destination_dir>
                                          -r <reference taxonomy>

    Generate database identifiers that match a list of expected taxonomies at
        species level. Expected taxonomies must be full-length taxonomy strings
        that match the given reference database, e.g., should be generated
        using autoannotate.py.

    -i / --infile: filepath
        tab-separated list of taxonomy strings in first column. Assumes that a
            header line exists, i.e., will skip first line of file.

    -o / --outfile: filepath
        destination in which to write database identifiers file

    -r / --ref_taxa: filepath
        tab-separated list of semicolon-delimited taxonomy strings
        associated with reference sequences. In format:
        seqID   taxonomy
        0001    kingdom;phylum;class;order;family;genus;species

    '''


def main(argv):
    source_fp = ''
    destination_fp = ''
    ref_taxa_fp = ''

    try:
        opts, args = getopt.getopt(argv, "hi:o:r:", ["help", "infile=",
                                                     "outdir=", "ref_taxa="])
    except getopt.GetoptError:
        print(usage)
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print(usage)
            sys.exit()
        elif opt in ("-i", "--infile"):
            source_fp = arg
        elif opt in ("-o", "--outdir"):
            destination_fp = arg
        elif opt in ("-r", "--ref_taxa"):
            ref_taxa_fp = arg

    # parse input file
    with open(source_fp, "r") as infile:
        infile.readline()
        source_taxa = [l.strip().split('\t')[0] for l in infile]

    ref_taxa = dict()
    # parse ref taxonomy
    with open(ref_taxa_fp, "r") as ref:
        for l in ref:
            i, t = l.strip().split('\t')
            if t not in ref_taxa.keys():
                ref_taxa[t] = [i]
            else:
                ref_taxa[t].append(i)

    # Pull identifiers from ref_taxa and write out
    with open(destination_fp, "w") as dest:
        for t in source_taxa:
            if t in ref_taxa.keys():
                dest.write('{0}\t{1}\n'.format(t, '\t'.join(ref_taxa[t])))


if __name__ == "__main__":
    main(sys.argv[1:])
