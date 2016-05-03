# mockrobiota data description

This document describes the data provided by mockrobiota for a single mock community dataset.

```
mockrobiota/
└── data
    └── example-1
        ├── dataset-metadata.tsv # dataset metadata
        ├── greengenes # database name
        │   └── 13_8 # database version
        │       ├── accession-numbers.tsv # accession numbers associated with this taxonomy
        │       └── expected-taxonomy.tsv # abundances in classic biom-format
        ├── sample-metadata.tsv # QIIME-compatible mapping file
        └── source
            └── taxonomy.tsv # abundances in classic biom-format, using provided names
            └── any other relevant files (if applicable, these should be relatively small to keep repo size reasonable)
```
