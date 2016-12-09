#!/usr/bin/env python

# ----------------------------------------------------------------------------
# Copyright (c) 2016--, mockrobiota development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------


from os.path import join, exists
from os import makedirs
import re
import sys, getopt


def add_lists(l1, l2):
    newlist = [sum(tup) for tup in zip(l1, l2)]
    return newlist


def main(argv):
    source_fp = ''
    destination_dir = ''
    ref_taxa_fp = ''
    try:
       opts, args = getopt.getopt(argv,"hi:o:r:",["infile=", "outdir=",
                                                 "ref_taxa="])
    except getopt.GetoptError:
        print('''usage: autoannotate-taxa.py -i <source_fp>\
                                             -o <destination_dir>
                                             -r <ref_taxa_fp>

            Type autoannotate-taxa.py -h for help menu.''')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('''usage: autoannotate-taxa.py -i <source_fp>\
                                              -o <destination_dir>
                                              -r <reference taxonomy>

                Generate full taxonomy strings from a reference database, given
                a list of "source" genus and species names.

                source_fp: filepath
                    tab-separated list of genus/species names and [optionally]
                    relative abundances in format:
                    Taxonomy    Sample1
                    Lactobacillus plantarum 0.5
                    Pediococcus damnosus    0.5

                destination_dir: path
                    directory in which to write annotated taxonomy file

                ref_taxa_fp: filepath
                    tab-separated list of semicolon-delimited taxonomy strings
                    associated with reference sequences. In format:
                    seqID   taxonomy
                    0001    kingdom;phylum;class;order;family;genus;species
                ''')

            sys.exit()
        elif opt in ("-i", "--infile"):
            source_fp = arg
        elif opt in ("-o", "--outdir"):
            destination_dir = arg
        elif opt in ("-r", "--ref_taxa"):
            ref_taxa_fp = arg


    # generate dict of {name: (genus, species, abundances)}
    with open(source_fp, "r") as source:
        sample_list = source.readline().strip().split('\t')[1:]
        taxa = {}
        for l in source:
            # convert abundances to float
            abundances = list(map(float, l.strip().split('\t')[1:]))
            name = l.strip().split('\t')[0]
            taxon = re.split(' |_', name.split(';')[-1])[0:2]
            taxa[name] = (taxon, abundances)

    # parse ref taxonomy
    with open(ref_taxa_fp, "r") as ref:
        ref_taxa = {l.strip().split('\t')[1]: (\
                        l.strip().split('\t')[1].split(';')[-2],
                        l.strip().split('\t')[1].split(';')[-1],
                        l.strip().split('\t')[0]
                        ) for l in ref}

    # find matching taxonomies
    species_match = 0
    genus_match = 0
    no_match = 0
    count = len(taxa)

    duplicates = []
    seq_ids = dict()
    new_taxa = dict()

    for name, t in taxa.items():
        match = 'None'

        # search for match at genus, then species level
        for full, partial in ref_taxa.items():
            if t[0][0] in partial[0]:
                if t[0][1] in partial[1]:
                    match = 'species'
                    seq_ids[full] = partial[2]
                    break
                else:
                    match = 'genus'
                    genus = ';'.join(full.split(';')[:-1])

        # now add match to new_taxa
        if match == 'species':
            species_match += 1
            if full not in new_taxa.keys():
                new_taxa[full] = (name, t[1])
            else:
                # if species is replicated, collapse abundances
                new_taxa[full] = (name, add_lists(new_taxa[full][1], t[1]))
                duplicates.append((name, full))

        elif match == 'genus':
            genus_match += 1
            if genus not in new_taxa.keys():
                new_taxa[genus] = (name, t[1])
            else:
                # if genus is replicated, collapse abundances
                new_taxa[genus] = (name, add_lists(new_taxa[genus][1], t[1]))
                duplicates.append((name, genus))

        # if failed, user needs to manually search and input new string
        else:
            no_match += 1
            print('\n\n{0} has no matches to {1}.'.format(name, ref_taxa_fp))
            print('Perform a manual search of your reference database to')
            print('match the nearest basal lineage. A good place to start is')
            print('NCBI taxonomy (https://www.ncbi.nlm.nih.gov/taxonomy) to')
            print('find the current accepted taxonomy, then use grep or')
            print('similar to search for the nearest lineage in your')
            print('reference. Assign the nearest basal lineage. For example,')
            print('if Lactobacillus casei has no species or genus-level')
            print('matches in the database, but Lactobacillales is present,')
            print('assign the taxonomy string up to Lactobacillales.')
            print('\nEnter the correct taxonomy for the basal lineage here:')
            lineage = input('> ')
            #failures.append(name)
            #new_taxa[name] = (name, t[1])
            if lineage not in new_taxa.keys():
                new_taxa[lineage] = (name, t[1])
            else:
                # if genus is replicated, collapse abundances
                new_taxa[lineage] = (name, add_lists(new_taxa[lineage][1],
                                                     t[1]))
                duplicates.append((name, lineage))

    # Print results
    print('{0} species-level matches ({1:.1f}%)'.format(species_match,
                                                      species_match/count*100))
    print('{0} genus-level matches ({1:.1f}%)'.format(genus_match,
                                                      genus_match/count*100))
    if no_match > 0:
        print('{0} FAILURES ({1:.1f}%)'.format(no_match, no_match/count*100))

    if len(duplicates) > 0:
        print('\n{0} duplicates:'.format(len(duplicates)))
        for dup in duplicates:
            print('{0}\t{1}'.format(dup[0], dup[1]))

    # Write to file
    if not exists(destination_dir):
        makedirs(destination_dir)

    with open(join(destination_dir, 'expected-taxonomy.tsv'), "w") as dest:
        dest.write('Taxonomy\t{0}\n'.format('\t'.join(sample_list)))
        for name, t in new_taxa.items():
            abundances = ["{:.10f}".format(n) for n in t[1]]
            dest.write('{0}\t{1}\n'.format(name, '\t'.join(abundances)))

    with open(join(destination_dir, 'database-identifiers.tsv'), "w") as dest:
        for t, seq_id in seq_ids.items():
            dest.write('{0}\t{1}\n'.format(t, seq_id))

    print('\n\nWARNING: it is your responsibility to ensure the accuracy of')
    print('all output files. Manually review the expected-taxonomy.tsv to')
    print('ensure that (1) all taxonomy strings are accurately represented')
    print('and (2) all relative abundances sum to 1.0')


if __name__ == "__main__":
   main(sys.argv[1:])
