#!/usr/bin/env python

# ----------------------------------------------------------------------------
# Copyright (c) 2016--, mockrobiota development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from os.path import expandvars, join, isdir
from os import listdir
from glob import glob


def generate_dataset_inventory(mockrobiota_dir):
    data_dir = join(mockrobiota_dir, 'data')
    inventory_fp = join(mockrobiota_dir, 'inventory.tsv')

    # count datasets
    count = len([i for i in listdir(data_dir) if isdir(join(data_dir, i))])

    # generate list of datasets to extract metadata
    communities = ['mock-{0}'.format(n) for n in range(1, count)]

    # Create dictionary of mock community dataset metadata
    community_metadata = extract_mockrobiota_dataset_metadata(mockrobiota_dir,
                                                              communities)
    # Iterate communities, extract metadata links
    inventory = [['StudyID', 'metadata', 'raw-data-url-forward-read',
                  'raw-data-url-reverse-read', 'raw-data-url-index-read',
                  'qiita-id', 'study-type', 'target-gene',
                  'human-readable-description']]
    for study_id in communities:
        # extract dataset metadata/params
        metadata = 'https://github.com/caporaso-lab/mockrobiota/tree/master/data/{0}/sample-metadata.tsv'.format(study_id)

        (raw_data_url_forward_read, raw_data_url_reverse_read,
            raw_data_url_index_read, qiita_id, study_type, target_gene,
            human_readable_description) = community_metadata[study_id]

        inventory.append([study_id, metadata, raw_data_url_forward_read,
                          raw_data_url_reverse_read, raw_data_url_index_read,
                          qiita_id, study_type, target_gene,
                          human_readable_description])

    with open(inventory_fp, "w") as inventory_fh:
        inventory_fh.write('\n'.join('\t'.join(v) for v in inventory))


def import_tsv_to_dict(infile):
    ''' taxonomy file -> dict'''
    with open(infile, "r") as inputfile:
        lines = {line.strip().split('\t')[0]: line.strip().split('\t')[1]
                 for line in inputfile}
    return lines


def extract_description(readme_fp):
    '''Extract human readable description from first paragraph of README.md'''
    with open(readme_fp, "r") as readme:
        for line in readme:
            if line.strip() and not line.startswith('#'):
                description = line.strip()
                break
    return description


def extract_mockrobiota_dataset_metadata(mockrobiota_dir, communities):
    '''Extract mock community metadata from mockrobiota dataset-metadata.tsv
    files
    mockrobiota_dir: PATH to mockrobiota directory
    communities: LIST of mock communities to extract
    '''
    dataset_metadata_dict = dict()
    for community in communities:
        dataset_dir = join(mockrobiota_dir, "data", community)
        dataset_metadata = import_tsv_to_dict(join(dataset_dir,
                                                   "dataset-metadata.tsv"))
        human_readable_description = extract_description(join(dataset_dir,
                                                              'README.md'))

        dataset_metadata_dict[community] = \
            (dataset_metadata['raw-data-url-forward-read'],
             dataset_metadata['raw-data-url-reverse-read'],
             dataset_metadata['raw-data-url-index-read'],
             dataset_metadata['qiita-id'],
             dataset_metadata['study-type'],
             dataset_metadata['target-gene'],
             human_readable_description
             )
    return dataset_metadata_dict


# How can we detect where mockrobiota is installed???
mockrobiota_dir = expandvars('$HOME/Desktop/projects/mockrobiota/')

# Generate list of dataset files that define inventory data. If these change,
# generate a new inventory below.
# Critical files are: dataset-metadata.tsv and sample-metadata.tsv
dataset_files = glob(join(mockrobiota_dir, 'data', '*', '*.tsv'))

# How to detect changes in current commit?
# if changes with current commit include file in dataset_files:
#   generate_dataset_inventory(mockrobiota_dir)

# line below is for test purposes until ln 105 is resolved
generate_dataset_inventory(mockrobiota_dir)
