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
import sys
import getopt


def add_lists(l1, l2):
    newlist = [sum(tup) for tup in zip(l1, l2)]
    return newlist


def choose_taxonomy(query_name, query_set, taxa_fp):
    print('\n\n{0} matches more than one unique taxonomy.'.format(query_name))
    print('Choose the valid taxonomy from the list below:\n')
    species_list = list(query_set)
    for num, item in enumerate(species_list):
        print(num, item)
    selection = input('\n\nChoose taxonomy number or "n" if none of these: ')
    if selection == 'n':
        full = manual_search(query_name, taxa_fp)
    else:
        selection = int(selection)
        full = species_list[selection]
    return full


def manual_search(query_name, taxa_fp):
            print('\n\n{0} has no matches to {1}.'.format(query_name, taxa_fp))
            print('Perform a manual search of your reference database to')
            print('match the nearest basal lineage.')
            print('\nEnter the correct taxonomy for the basal lineage here:')
            lineage = input('> ')
            return lineage


usage = '''usage: autoannotate-taxa.py -i <source_fp>
                                  -o <destination_dir>
                                  -r <reference taxonomy>
                                  -p <string separator>
                                  -g <genus placeholder>
                                  -s <species placeholder>

    Generate full taxonomy strings from a reference database, given
    a list of "source" genus and species names.

    -i / --infile: filepath
        tab-separated list of genus/species names and [optionally]
        relative abundances in format:
        Taxonomy    Sample1
        Lactobacillus plantarum 0.5
        Pediococcus damnosus    0.5

    -o / --outfile: path
        directory in which to write annotated taxonomy file

    -r / --ref_taxa: filepath
        tab-separated list of semicolon-delimited taxonomy strings
        associated with reference sequences. In format:
        seqID   taxonomy
        0001    kingdom;phylum;class;order;family;genus;species

    -p / --separator: str
        taxonomy strings are separated with this string pattern.
        Default = ";"

    -g / --genus: str
        Placeholder to use for taxa that have no genus-level match
        in reference taxonomy file. Should match the conventions
        that are used in that reference taxonomy file.
        Default = "g__"

    -s / --species: str
        Placeholder to use for taxa that have no species-level match
        in reference taxonomy file. Should match the conventions
        that are used in that reference taxonomy file.
        Default = "s__"

    '''


def main(argv):
    source_fp = ''
    destination_dir = ''
    ref_taxa_fp = ''
    sep = ';'
    gen = 'g__'
    sp = 's__'

    try:
        opts, args = getopt.getopt(argv, "hi:o:r:p:g:s:", ["help",
                                                           "infile=",
                                                           "outdir=",
                                                           "ref_taxa=",
                                                           "separator",
                                                           "genus",
                                                           "species"])
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
            destination_dir = arg
        elif opt in ("-r", "--ref_taxa"):
            ref_taxa_fp = arg
        elif opt in ("-p", "--separator"):
            sep = arg
        elif opt in ("-g", "--genus"):
            gen = arg
        elif opt in ("-s", "--species"):
            sp = arg

    # generate dict of {name: (genus, species, abundances)}
    with open(source_fp, "r") as source:
        sample_list = source.readline().strip().split('\t')[1:]
        taxa = {}
        for l in source:
            # convert abundances to float
            abundances = list(map(float, l.strip().split('\t')[1:]))
            name = l.strip().split('\t')[0]
            # level labels (e.g., Silva's 'D_11__') can confabulate this.
            # Hence, do split on '__' instead of sep to remove level labels
            taxon = re.split(' |_', name.split(';')[-1])[0:2]
            if name not in taxa.keys():
                taxa[name] = (taxon, abundances)
            else:
                # if species is replicated, collapse abundances
                taxa[name] = (taxon, add_lists(taxa[name][1], abundances))

    # parse ref taxonomy
    with open(ref_taxa_fp, "r") as ref:
        ref_taxa = {l.strip().split('\t')[1]: (
                        l.strip().split('\t')[1].split(sep)[-2],
                        l.strip().split('\t')[1].split(sep)[-1],
                        l.strip().split('\t')[0]
                        ) for l in ref}

    # find matching taxonomies
    species_match = 0
    genus_match = 0
    family_match = 0
    no_match = 0
    count = len(taxa)

    duplicates = []
    seq_ids = dict()
    new_taxa = dict()

    for name, t in taxa.items():
        species_set = set()
        genus_set = set()
        match = 'None'

        # search for match at genus, then species level
        for full, partial in ref_taxa.items():
            if t[0][0] in partial[0]:
                if t[0][1] in partial[1]:
                    match = 'species'
                    species_set.add(full)
                    if full not in seq_ids:
                        seq_ids[full] = [partial[2]]
                    else:
                        seq_ids[full].append(partial[2])
                elif match != 'species':
                    match = 'genus'
                    genus_set.add(sep.join(full.split(sep)[:-1]) + sep + sp)

        # If no species or genus matches, make attempt at family level
        if match == 'None':
            if t[0][0].endswith('er'):
                family = '{0}iaceae'.format(t[0][0])
            elif t[0][0].endswith('ma'):
                family = t[0][0] + 'taceae'
            elif t[0][0].endswith('a'):
                family = t[0][0] + 'ceae'
            elif t[0][0].endswith('myces'):
                family = t[0][0][:-1] + 'taceae'
            elif t[0][0].endswith('es'):
                family = t[0][0][:-2] + 'aceae'
            elif t[0][0].endswith('thece'):
                family = t[0][0][:-1] + 'aceae'
            elif t[0][0].endswith('stis'):
                family = t[0][0][:-2] + 'aceae'
            elif t[0][0].endswith('as') or t[0][0].endswith('is'):
                family = t[0][0][:-1] + 'daceae'
            elif t[0][0].endswith('us') or t[0][0].endswith('um'):
                family = t[0][0][:-2] + 'aceae'
            elif t[0][0].endswith('io'):
                family = t[0][0] + 'naceae'
            # Homoeothrix Crenothrix Erysipelothrix Thiothrix
            elif t[0][0].endswith('thrix'):
                family = t[0][0][:-4] + 'richaceae'
            # Cyanothrix Tolypothrix
            elif t[0][0].endswith('Cyanothrix') or t[0][0].endswith('pothrix'):
                family = t[0][0][:-1] + 'chaceae'
            elif t[0][0].endswith('ex'):
                family = t[0][0][:-2] + 'icaceae'
            else:
                family = t[0][0] + 'aceae'

            for full in ref_taxa.keys():
                if family in full.split(sep)[-3]:
                    match = 'family'
                    family = sep.join([sep.join(full.split(sep)[:-2]),
                                      gen, sp])
                    print('\n\n', name, ' nearest match to family level:')
                    print(family, '\n\n')
                    approval = input('Do you approve? (y/n): ')
                    if approval == 'y':
                        break

        # now add match to new_taxa
        if match == 'species':
            species_match += 1

            if len(species_set) > 1:
                species = choose_taxonomy(name, species_set, ref_taxa_fp)
            else:
                species = list(species_set)[0]

            if species not in new_taxa.keys():
                new_taxa[species] = (name, t[1])
            else:
                # if species is replicated, collapse abundances
                new_taxa[species] = (name,
                                     add_lists(new_taxa[species][1], t[1]))
                duplicates.append((name, species))

        elif match == 'genus':
            genus_match += 1

            if len(genus_set) > 1:
                genus = choose_taxonomy(name, genus_set, ref_taxa_fp)
            else:
                genus = list(genus_set)[0]

            if genus not in new_taxa.keys():
                new_taxa[genus] = (name, t[1])
            else:
                # if genus is replicated, collapse abundances
                new_taxa[genus] = (name, add_lists(new_taxa[genus][1], t[1]))
                duplicates.append((name, genus))

        elif match == 'family':
            family_match += 1

            if family not in new_taxa.keys():
                new_taxa[family] = (name, t[1])
            else:
                # if genus is replicated, collapse abundances
                new_taxa[family] = (name, add_lists(new_taxa[family][1], t[1]))
                duplicates.append((name, family))

        # if failed, user needs to manually search and input new string
        else:
            no_match += 1

            lineage = manual_search(name, ref_taxa_fp)
            if lineage not in new_taxa.keys():
                new_taxa[lineage] = (name, t[1])
            else:
                # if genus is replicated, collapse abundances
                new_taxa[lineage] = (name, add_lists(new_taxa[lineage][1],
                                                     t[1]))
                duplicates.append((name, lineage))

    # Print results
    print('{0} species-level matches ({1:.1f}%)'.format(
        species_match, species_match/count*100))
    print('{0} genus-level matches ({1:.1f}%)'.format(genus_match,
                                                      genus_match/count*100))
    if family_match > 0:
        print('{0} family-level matches ({1:.1f}%)'.format(
            family_match, family_match/count*100))
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
            dest.write('{0}\t{1}\n'.format(t, '\t'.join(seq_id)))

    print('\n\nWARNING: it is your responsibility to ensure the accuracy of')
    print('all output files. Manually review the expected-taxonomy.tsv to')
    print('ensure that (1) all taxonomy strings are accurately represented')
    print('and (2) all relative abundances sum to 1.0')


if __name__ == "__main__":
    main(sys.argv[1:])
