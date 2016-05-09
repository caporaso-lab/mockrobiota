#!/usr/bin/env python

import os
import csv
import sys
import glob
import os.path
import unittest
import urllib.error
import urllib.request

BAD_URLS_FP = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           'bad-urls.txt')

# TODO clean up this code
class CheckDataIntegrity(unittest.TestCase):
    def test_directory_structure(self):
        data_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'data')
        self.assertTrue(os.path.isdir(data_dir),
                        "Data directory %r does not exist" % data_dir)

        for dataset_dir in glob.glob(os.path.join(data_dir, '*')):
            self.assertTrue(os.path.isdir(dataset_dir),
                            "%r is not a directory. All paths under %r must be dataset-specific directories." % (dataset_dir, data_dir))

            dataset_metadata_fp = os.path.join(dataset_dir, 'dataset-metadata.tsv')
            self.assertTrue(os.path.isfile(dataset_metadata_fp),
                            "Dataset metadata %r does not exist" % dataset_metadata_fp)
            self._assert_valid_dataset_metadata_file(dataset_metadata_fp)

            sample_metadata_fp = os.path.join(dataset_dir, 'sample-metadata.tsv')
            self.assertTrue(os.path.isfile(sample_metadata_fp),
                            "Sample metadata %r does not exist" % sample_metadata_fp)

            source_dir = os.path.join(dataset_dir, 'source')
            if os.path.isdir(source_dir):
                source_taxonomy_fp = os.path.join(source_dir, 'taxonomy.tsv')
                self.assertTrue(os.path.isfile(source_taxonomy_fp),
                                "Source taxonomy %r does not exist" % source_taxonomy_fp)
                self._assert_valid_taxonomy_file(source_taxonomy_fp)

            db_dirs = []
            for path in glob.glob(os.path.join(dataset_dir, '*')):
                if os.path.basename(path) != 'source' and os.path.isdir(path):
                    db_dirs.append(path)

            for db_dir in db_dirs:
                db_version_dirs = glob.glob(os.path.join(db_dir, '*'))
                self.assertTrue(len(db_version_dirs) > 0,
                                "Database directory %r must have at least one database version-specific subdirectory." % db_dir)

                for db_version_dir in db_version_dirs:
                    self.assertTrue(os.path.isdir(db_version_dir),
                                    "%r is not a directory. All paths under %r must be database version-specific directories." % (db_version_dir, db_dir))

                    expected_taxonomy_fp = os.path.join(db_version_dir, 'expected-taxonomy.tsv')
                    self.assertTrue(os.path.isfile(expected_taxonomy_fp),
                                    "Expected taxonomy %r does not exist" % expected_taxonomy_fp)

                    expected_taxonomy_column = self._assert_valid_taxonomy_file(expected_taxonomy_fp)

                    db_id_fp = os.path.join(db_version_dir,
                                            'database-identifiers.tsv')
                    if os.path.isfile(db_id_fp):
                        db_id_taxonomy_column = self._assert_valid_database_id_file(db_id_fp)
                        self._assert_compatible_taxonomy_columns(expected_taxonomy_fp, expected_taxonomy_column, db_id_fp, db_id_taxonomy_column)

    def _assert_valid_dataset_metadata_file(self, fp):
        with open(fp, newline='') as fh:
            rows = list(csv.reader(fh, delimiter='\t'))
            header = rows[0]
            self.assertEqual(header, ['name', 'value'],
                    "Dataset metadata file %r: header must be 'name\\tvalue'" % fp)
            rows = rows[1:]

            name_value_map = {}
            for row in rows:
                self.assertEqual(len(row), 2,
                                 "Dataset metadata file %r: each row must contain exactly two values, not %r" % (fp, len(row)))
                name, value = row
                self.assertFalse(name in name_value_map,
                                 "Dataset metadata file %r: 'name' column must be unique, found duplicate cell %r" % (fp, name))
                required_values = ['raw-data-url']
                if name in required_values:
                    self.assertTrue(value,
                                    "Dataset metadata file %r: the value for %r cannot be empty." % (fp, name))
                    self.assertNotEqual(value, 'NA',
                                        "Dataset metadata file %r: the value for %r cannot be NA." % (fp, name))
                else:
                    self.assertTrue(value,
                                    "Dataset metadata file %r: the value for %r cannot be empty (use NA instead)" % (fp, name))
                name_value_map[name] = value

            required_names = [
                'citation', 'qiita-id', 'raw-data-url',
                'human-readable-description', 'bokulich2013-id',
                'bokulich2015-id', 'target-gene', 'target-subfragment',
                'study-type', 'sequencing-instrument',
                'physical-specimen-available', 'physical-specimen-contact']
            self.assertCountEqual(list(name_value_map.keys()), required_names)

            raw_data_url = name_value_map['raw-data-url']
            try:
                urllib.request.urlopen(raw_data_url)
            except urllib.error.URLError:
                with open(BAD_URLS_FP, 'a') as f:
                    f.write("%s : %s" % (fp, raw_data_url))
                    f.write("\n")

    def _assert_valid_taxonomy_file(self, fp):
        with open(fp, newline='') as fh:
            rows = list(csv.reader(fh, delimiter='\t'))
            header = rows[0]
            rows = rows[1:]

            self.assertEqual(header[0], "#Taxonomy",
                    "Taxonomy file %r: top-left cell must be #Taxonomy, not %r" % (fp, header[0]))

            sample_ids = header[1:]
            self.assertEqual(len(sample_ids), len(set(sample_ids)),
                    "Taxonomy file %r: sample IDs in taxonomy file must be unique" % fp)

            taxonomy_column = []
            for row in rows:
                self.assertEqual(len(row), len(header),
                                 "Taxonomy file %r: each row must have the same number of cells as the header" % fp)
                taxonomy_column.append(row[0])
            self.assertEqual(len(taxonomy_column), len(set(taxonomy_column)),
                    "Taxonomy file %r: taxonomy column values must be unique" % fp)

            for sample_id, column in zip(sample_ids, list(zip(*rows))[1:]):
                column = [float(value) for value in column]
                column_sum = sum(column)
                self.assertAlmostEqual(column_sum, 1.0, delta=0.001,
                        msg="Taxonomy file %r: sample ID %r must have taxa frequencies that sum to 1.0, not %r" % (fp, sample_id, column_sum))

            return taxonomy_column

    def _assert_valid_database_id_file(self, fp):
        with open(fp, newline='') as fh:
            rows = list(csv.reader(fh, delimiter='\t'))

            taxonomy_column = [row[0] for row in rows]
            self.assertEqual(len(taxonomy_column), len(set(taxonomy_column)),
                    "Database identifiers file %r: taxonomy column values must be unique" % fp)

            return taxonomy_column

    def _assert_compatible_taxonomy_columns(self, fp1, column1, fp2, column2):
        self.assertCountEqual(column1, column2,
                              "Taxonomy columns in %r and %r must have the same values (having the same order is not required)" % (fp1, fp2))


if __name__ == '__main__':
    test_program = unittest.main(exit=False)

    if os.path.exists(BAD_URLS_FP):
        sys.stderr.write('\nSome URLs could not be reached:\n')
        with open(BAD_URLS_FP) as f:
            bad_url_messages = f.read()
        os.remove(BAD_URLS_FP)
        sys.exit(bad_url_messages)

    if test_program.result.wasSuccessful():
        sys.exit(0)
    else:
        sys.exit(1)
