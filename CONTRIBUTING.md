# Contributing to mockrobiota

[mockrobiota](https://github.com/caporaso-lab/mockrobiota) is a public resource that depends on community involvement to grow and evolve. Thank you for sharing your awesome mock communities with the world.

This document describes how to get started with contributing to mockrobiota. Please read the entire document before contributing to mockrobiota, to save time for both you and the mockrobiota developers.

## Types of contributions

The main contributions to mockrobiota should be:

1. a new mock community that has not yet been submitted to mockrobiota.
2. a new resource for a mock community that already exists in mockrobiota. For example, reference sequences for each member of a mock community already existing in mockrobiota, or taxonomic annotations according to a new database or database version.
3. a revision to an existing resource for a mock community in mockrobiota. For example, if errors are discovered in a file already submitted to mockrobiota.

The necessary file types and naming conventions for contributing mock community resources are described below in [Contributing mock community resources](#contributing-mock-community-resources). The steps required for submitting these and all other contribution types are listed below in [Submitting to mockrobiota](#submitting-to-mockrobiota). Other contributions may also be appropriate, such as feature additions or bug fixes (in this case, a bug would likely be incorrect data in the repository).

For all contribution types, the best way to begin is by posting the issue to the [mockrobiota issue tracker](https://github.com/caporaso-lab/mockrobiota/issues). When posting an issue, please describe the problem in detail, and (for feature additions) describe why the added functionality is relevant to mockrobiota. When you post your issue, the mockrobiota developers will respond to let you know if we agree with the addition or change. It's very important that you go through this step to avoid wasting time working on a feature that we are not interested in including in mockrobiota.

## Contributing mock community resources

New mock communities, resources, and resource revisions must adhere to the directory structure and formatting guidelines for mockrobiota. Before making any of these contributions, spend some time examining the directory structure and formatting of pre-existing datasets in mockrobiota. An example directory exists at [``mockrobiota/data/example-1/``](https://github.com/caporaso-lab/mockrobiota/tree/master/data/example-1) but other pre-existing datasets may also serve as useful templates.

### Directory structure

All mock communities are contained in unique directories and assigned an identifier in sequential order of submission to mockrobiota. The directory structure follows the convention
``mockrobiota/data/dataset-name/``. For example, all files associated with the ``mock-1`` data set are in [``mockrobiota/data/mock-1/``](https://github.com/caporaso-lab/mockrobiota/tree/master/data/mock-1). An example mock community directory structure looks like the following:

```
mockrobiota/
└── data
    └── example-1
        ├── dataset-metadata.tsv # dataset metadata
        ├── greengenes # database name
        │   └── 13_8 # database version
        │       ├── database-identifiers.tsv # database identifiers associated with each mock community member (optional)
        │       └── expected-taxonomy.tsv # per-sample taxonomic abundances
        ├── sample-metadata.tsv # QIIME-compatible mapping file
        └── source
            └── taxonomy.tsv # per-sample taxonomic abundances
            └── any other relevant files (if applicable, these should be relatively small to keep repo size reasonable)
```



Each mock community directory contains the following directories and file types:

### ``dataset-metadata.tsv``
Contains metadata for a mock community dataset, as well as links for downloading raw data. This file contains TAB-separated (key, value) pairs, with each (key, value) pair on a separate line and separated by a tab. Unless otherwise noted, you can provide ``NA`` to indicate that a required field is not applicable.

The required fields are:

* ``citation``: DOI, PubMed Identifier (PMID), or direct link for original citation.
* ``qiita-id``: Study ID for raw data submitted to [QIITA database](https://qiita.ucsd.edu/).
* ``raw-data-url-forward-read``: Direct link to raw data **forward** sequences submitted to other public repositories. A valid, working URL must be provided. ``NA`` is not a permitted value for this field. See information below about formatting and depositing raw data.
* ``raw-data-url-reverse-read``: Direct link to raw data **reverse** sequences submitted to other public repositories. This field is **optional** and if no reverse reads exist, list ``NA`` as the value for this field. See information below about formatting and depositing raw data.
* ``raw-data-url-index-read``: Direct link to raw data **index** sequences (a.k.a. barcode reads) submitted to other public repositories. A valid, working URL must be provided. ``NA`` is not a permitted value for this field. See information below about formatting and depositing raw data.
* ``human-readable-description``: A description of the mock community dataset. At minimum, should include the number and types (bacterial, eukaryotic, archaeal, etc) of strains included in the mock community; the number of sample replicates; the investigators responsible for creating the mock community; and the main institution where this mock community was generated. Include as much relevant information as possible. If relevant, indicate the features that are common to or different across the samples included in the dataset (for example, if all are replicates of the same sample); the number of unique samples included; whether strains were mixed at even or uneven ratios; and whether the samples in this mock community are included in any other mock communities, and if so, whether those are marker-gene or metagenome mock communities (or another mock community type).
* ``bokulich2013-id``: This only applies to the founder datasets included in mockrobiota, and indicates the mock community ID used in the [original citation](http://www.nature.com/nmeth/journal/v10/n1/abs/nmeth.2276.html). New mock communities should list ``NA`` as the value for this field.
* ``bokulich2015-id``: This only applies to the founder datasets included in mockrobiota, and indicates the mock community ID used in the [original citation](https://dx.doi.org/10.7287/peerj.preprints.934v2). New mock communities should list ``NA`` as the value for this field.
* ``target-gene``: The marker gene analyzed in this mock community dataset, for example, 16S, 18S, ITS. For other study types, list NA.
* ``target-subfragment``: The subregion of the marker gene analyzed. E.g., V4 (a subregion of 16S rRNA). For other study types, list NA.
* ``study-type``: The type of study. Should be ``marker-gene`` or ``metagenome``. Other analysis types are theoretically possible. If submitting a mock community that is neither marker-gene sequences nor shotgun metagnome sequences, [create an issue](https://github.com/caporaso-lab/mockrobiota/issues) to confer with the mockrobiota developers before proceeding.
* ``sequencing-instrument``: The sequencing method used for analysis, for example, ``illumina-hiseq``. We do not have an established naming convention here, but may make suggestions to help keep these consistent across data sets.
* ``physical-specimen-available``: Does a physical specimen exist for this mock community and is it available for other investigators to request aliquots? Value should be ``Yes`` or ``No``.
* ``contact-email``: Provide a contact email to which other investigators should direct their questions and requests.

### ``sample-metadata.tsv``
This file lists metadata for each individual sample contained in a mock community dataset, e.g., replicates of the same mock community or other mock communities included in the same sequencing run. This is a tab-separated text file, in [QIIME 1 mapping file format](http://qiime.org/documentation/file_formats.html#metadata-mapping-files). The [Keemei Google Sheets](http://keemei.qiime.org) plugin can be used to validate this file. The minimum requirements for marker-gene and metagenome mock communities are:

* ``SampleID``: Sample identifier which is unique within this mock community.
* ``BarcodeSequence``: Unique barcode (i.e., index) sequence for each sample.
* ``LinkerPrimerSequence``: Forward primer sequence (mock marker-gene studies only, include ``NA`` if this is not applicable).
* ``ReversePrimer``: reverse primer sequence (mock marker-gene studies only, include ``NA`` if this is not applicable).
* ``PrimerName``: Forward and reverse primer names. We recommend using the format ``Xf-Yr``, where ``X`` is the forward primer name and ``Y`` is the reverse primer name. For example, 515f-806r. (Mock marker-gene studies only, include ``NA`` if this is not applicable.)
* ``Description``: Description for each sample, usually around 1-5 words.

### ``source/taxonomy.tsv`` (optional)
This file lists the taxonomic and (when possible) strain affiliation of each strain added to the mock community, as well as its relative abundance. This file does not need to adhere to a particular taxonomic reference database, but please include as much information as possible (e.g., if this strain is available through a public repository, please list the repository strain ID). This information is usually provided by the developer(s) of the mock community.

In these files, the first line must begin with the text ``Taxonomy``, followed by a tab-separated list of one or more sample identifiers. All sample identifiers provided here must be present in ``sample-metadata.tsv``. Each subsequent line should begin with the taxonomic name, followed by a tab-separated list of the relative abundances in each sample. The relative abundances must sum to 1.000 (to three decimal places) for each sample. See [source taxonomy.tsv](./data/example-1/source/taxonomy.tsv) for an example file.

### Expected taxonomy (``database-name/database-version/expected-taxonomy.tsv``)
Contains the known composition of the mock community (e.g., taxonomies or KEGG pathways), annotated according to a specific reference database. Compilation of expected composition data is not a trivial task, and requires careful review of database annotations to ensure that accurate annotations are applied to source data. See [Compiling expected taxonomy files](#compiling-expected-taxonomy-files) below for discussion of this topic.

In these files, the first line must begin with the text ``Taxonomy``, followed by a tab-separated list of one or more sample identifiers. All sample identifiers provided here must be present in ``sample-metadata.tsv``. Each subsequent line should begin with the taxonomic name, followed by a tab-separated list of the relative abundances in each sample. The relative abundances must sum to 1.000 (to three decimal places) for each sample. See [example expected-taxonomy.tsv](./data/example-1/greengenes/13_8/expected-taxonomy.tsv) for an example file.

### Database identifiers (``database-name/database-version/database-identifiers.tsv``; optional)
Contributors may provide database identifiers associated with each member of the mock community (useful, for example, for identifying associated sequences in the reference database). Each taxonomic name listed in the ``expected-taxonomy.tsv`` in the same directory must be included, and can have zero or more database identifiers associated with it. The taxonomic name and all database identifiers should be separated by tabs.


## Raw Data

mockrobiota does not host raw data files (e.g., sequencing files). All sequencing data and other raw data files must be deposited on public, external websites. Stable, public depositories are preferred, but this requirement is not enforced by mockrobiota. mockrobiota ensures that valid, accessible links are provided in the dataset metadata (if not, integrity checks will fail and your dataset will not be accepted), but does not manage these external resources and can not guarantee the validity of raw data that are contributed by outside users. When preparing raw data for linking to mockrobiota datasets, please observe the following regulations:

1. All raw sequence data should be deposited in .fastq format and archived using standard compression formats, e.g., .gz or .zip.
2. Mock community datasets that contain multiple samples must be provided in non-demultiplexed files (i.e., one file per read direction per sequencing run, containing multiple uniquely barcoded samples).
3. Index/barcode sequences must be provided as a separate .fastq file. If QUAL scores do not exist for these reads, please note this in the human-readable-description field of dataset-metadata.tsv for that dataset.
4. Reverse sequencing reads are accepted, but not required. Forward and reverse reads should be submitted as separate files, not as joined reads.
5. All raw data must conform to the following naming conventions:
    - mock-forward-read.fastq.gz
    - mock-reverse-read.fastq.gz (if applicable)
    - mock-index-read.fastq.gz

## Submitting to mockrobiota
mockrobiota is hosted on [GitHub](http://www.github.com), and we use GitHub's [Pull Request](https://help.github.com/articles/using-pull-requests) mechanism for reviewing and accepting submissions. On submission of a pull request, a series of tests will be run to confirm the integrity of the submitted data (as well as to re-test the integrity of all existing data). We require these tests to pass for your data set before we will merge it to ensure the overall integrity of the mockrobiota resource.

## Compiling expected taxonomy files

Expected composition data will consist of one of the following types:

* Marker-gene mock community: expected taxonomic composition for a mixture of microbial cells. The taxonomic annotations present in the expected data will be specific to the database version that is used for analysis, and will be meaningless if used for different database versions. Likewise, they may not match the source annotation (i.e., the taxonomy of each strain to the best knowledge of the mock community’s creator) if taxonomic annotations have been revised or if the reference database being used does not contain a given taxonomy.
* Metagenome mock community: expected gene composition for a mixture of microbial cells/genomes. Gene annotations will be reference database specific, as for marker-gene mock communities above.

Other mock community data types are theoretically possible, and could be included in mockrobiota, which only defines required information, files, and file formats. Expected data definitions can expand as other mock community data types are contributed to mockrobiota. If submitting a mock community that is neither marker-gene sequences nor shotgun metagnome sequences, submit an [issue](https://github.com/caporaso-lab/mockrobiota/issues) to confer with the mockrobiota developers before proceeding.

Here we illustrate how expected taxonomy might be compiled from source taxonomy for an example dataset.

Source composition:

| #Taxonomy | sample1 |
|---------------------------------------|:-------:|
| Staphylococcus aureus ATCC BAA-1718 | 0.200 |
| Staphylococcus epidermidis ATCC 12228 | 0.200 |
| Streptococcus agalactiae ATCC BAA-611 | 0.200 |
| Streptococcus mutans ATCC 700610 | 0.200 |
| Streptococcus pneumoniae ATCC BAA-334 | 0.200 |


Expected composition, annotated with Greengenes 13_5 reference taxonomy:

| #Taxonomy | sample1 |
|------------------------------------------------------------------------------------------------------------|:-------:|
| k__Bacteria;p__Firmicutes;c__Bacilli;o__Bacillales;f__Staphylococcaceae;g__Staphylococcus aureus | 0.200 |
| k__Bacteria;p__Firmicutes;c__Bacilli;o__Bacillales;f__Staphylococcaceae;g__Staphylococcus;s__epidermidis | 0.200 |
| k__Bacteria;p__Firmicutes;c__Bacilli;o__Lactobacillales;f__Streptococcaceae;g__Streptococcus;s__ | 0.400 |
| k__Bacteria;p__Firmicutes;c__Bacilli;o__Lactobacillales;f__Streptococcaceae;g__Streptococcus;s__agalactiae | 0.200 |

Several issues may arise during database annotation that require careful attention, and hence careful manual curation of expected composition files is important:

* Specific taxa may not be represented in a reference taxonomy to species level and must be annotated to the nearest common lineage. For example, *Streptococcus mutans* and *Streptococcus pneumoniae* are annotated as *g__Streptococcus;s__* in the example above.
* Multiple input strains, listed as separate entities in the “source” files, may need to be combined under common annotations in the “expected composition” files if they are not listed in the reference database. The relative abundance of an expected taxonomy will be equal to the sum of all members matching that taxonomy. For example, multiple strains may be combined as a single species, or species not listed in the reference database may be combined under a single genus; note the relative abundance of *g__Streptococcus;s__* listed in the example above.
* Reference databases may contain quirks that complicate annotation of expected composition files, such as listing strain IDs or different taxonomic lineages for multiple entries of the same species. Contributors should carefully inspect reference database annotations and all expected composition files.

**Before submitting mock community resources to mockrobiota, please ensure that**:

* Taxonomy strings (or other annotations) for each strain match actual strings contained in the reference database used.
* Reference database names and versions are correct.
* Relative abundances of each strain sum to 1.000 (to three decimal places) for each sample in the mock community. Our automated data integrity checks will also test this.
* dataset-metadata.tsv lists only valid, publicly accessible URLs.
