#!/usr/bin/env python

import os
import csv
import sys
import glob
import os.path
import unittest
import urllib.error
import urllib.request

BAD_URLS = []


class CheckDataIntegrity(unittest.TestCase):
    def test_data_integrity(self):
        data_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'data')
        self.assertTrue(os.path.isdir(data_dir),
                        "Data directory %r does not exist" % data_dir)

        for dataset_dir in glob.glob(os.path.join(data_dir, '*')):
            self.assertTrue(os.path.isdir(dataset_dir),
                            "%r is not a directory. All paths under %r must "
                            "be dataset-specific directories." %
                            (dataset_dir, data_dir))

            dataset_metadata_fp = os.path.join(dataset_dir,
                                               'dataset-metadata.tsv')
            self._assert_valid_dataset_metadata_file(dataset_metadata_fp)

            sample_metadata_fp = os.path.join(dataset_dir,
                                              'sample-metadata.tsv')
            sample_ids = self._assert_valid_sample_metadata_file(
                sample_metadata_fp)

            source_dir = os.path.join(dataset_dir, 'source')
            if os.path.isdir(source_dir):
                source_taxonomy_fp = os.path.join(source_dir, 'taxonomy.tsv')
                self._assert_valid_taxonomy_file(source_taxonomy_fp,
                                                 sample_ids)

            db_dirs = []
            for path in glob.glob(os.path.join(dataset_dir, '*')):
                if os.path.basename(path) != 'source' and os.path.isdir(path):
                    db_dirs.append(path)

            for db_dir in db_dirs:
                db_version_dirs = glob.glob(os.path.join(db_dir, '*'))
                self.assertTrue(len(db_version_dirs) > 0,
                                "Database directory %r must have at least one "
                                "database version-specific subdirectory." %
                                db_dir)

                for db_version_dir in db_version_dirs:
                    self.assertTrue(
                        os.path.isdir(db_version_dir),
                        "%r is not a directory. All paths under %r must be "
                        "database version-specific directories." %
                        (db_version_dir, db_dir))

                    expected_taxonomy_fp = os.path.join(
                        db_version_dir, 'expected-taxonomy.tsv')
                    expected_taxonomy_ids = self._assert_valid_taxonomy_file(
                        expected_taxonomy_fp, sample_ids)

                    db_id_fp = os.path.join(db_version_dir,
                                            'database-identifiers.tsv')
                    if os.path.isfile(db_id_fp):
                        self._assert_valid_database_id_file(
                            db_id_fp, expected_taxonomy_fp,
                            expected_taxonomy_ids)

    def _assert_valid_dataset_metadata_file(self, fp):
        error_msg_prefix = "Dataset metadata file %r: " % fp
        self.assertTrue(os.path.isfile(fp),
                        error_msg_prefix + "file does not exist")

        with open(fp, newline='') as fh:
            rows = list(csv.reader(fh, delimiter='\t'))
            header = rows[0]
            self.assertEqual(
                header, ['name', 'value'],
                error_msg_prefix + "header must be 'name\\tvalue'")

            rows = rows[1:]
            name_value_map = {}
            for row in rows:
                self.assertEqual(len(row), 2,
                                 error_msg_prefix +
                                 "each row must contain exactly two values, "
                                 "not %d" % len(row))

                name, value = row
                self.assertFalse(name in name_value_map,
                                 error_msg_prefix +
                                 "'name' column must be unique, found "
                                 "duplicate cell %r" % name)

                required_values = ['raw-data-url']
                if name in required_values:
                    self.assertTrue(value,
                                    error_msg_prefix +
                                    "the value for %r cannot be empty." % name)

                    self.assertNotEqual(
                        value, 'NA',
                        error_msg_prefix +
                        "the value for %r cannot be NA." % name)
                else:
                    self.assertTrue(value,
                                    error_msg_prefix +
                                    "the value for %r cannot be empty (use NA "
                                    "instead)" % name)
                name_value_map[name] = value

            required_names = {
                'citation', 'qiita-id', 'raw-data-url',
                'human-readable-description', 'bokulich2013-id',
                'bokulich2015-id', 'target-gene', 'target-subfragment',
                'study-type', 'sequencing-instrument',
                'physical-specimen-available', 'physical-specimen-contact'}
            present_names = set(name_value_map.keys())
            self.assertTrue(required_names.issubset(present_names),
                            error_msg_prefix +
                            "missing the following required names: %r"
                            % (required_names - present_names))

            raw_data_url = name_value_map['raw-data-url']
            try:
                urllib.request.urlopen(raw_data_url)
            except urllib.error.URLError:
                BAD_URLS.append((fp, raw_data_url))

    def _assert_valid_sample_metadata_file(self, fp):
        error_msg_prefix = "Sample metadata file %r: " % fp
        self.assertTrue(os.path.isfile(fp),
                        error_msg_prefix + "file does not exist")

        with open(fp, newline='') as fh:
            rows = list(csv.reader(fh, delimiter='\t'))
            header = rows[0]
            rows = rows[1:]

            self.assertEqual(
                header[:3],
                ['#SampleID', 'BarcodeSequence', 'LinkerPrimerSequence'],
                error_msg_prefix +
                "header must start with "
                "'#SampleID\\tBarcodeSequence\\tLinkerPrimerSequence'")

            self.assertEqual(header[-1], 'Description',
                             error_msg_prefix +
                             "header must end with 'Description' column")

            sample_id_column = []
            for row in rows:
                self.assertEqual(len(row), len(header),
                                 error_msg_prefix +
                                 "each row must have the same number of cells "
                                 "as the header")
                sample_id_column.append(row[0])

            sample_ids = set(sample_id_column)
            self.assertEqual(len(sample_id_column), len(sample_ids),
                             error_msg_prefix + "sample IDs must be unique")

            return sample_ids

    def _assert_valid_taxonomy_file(self, fp, expected_sample_ids):
        error_msg_prefix = "Taxonomy file %r: " % fp
        self.assertTrue(os.path.isfile(fp),
                        error_msg_prefix + "file does not exist")

        with open(fp, newline='') as fh:
            rows = list(csv.reader(fh, delimiter='\t'))
            header = rows[0]
            rows = rows[1:]

            self.assertEqual(
                header[0],
                "#Taxonomy",
                error_msg_prefix +
                "top-left cell must be #Taxonomy, not %r" % header[0])

            sample_ids = set(header[1:])
            self.assertEqual(len(header[1:]), len(sample_ids),
                             error_msg_prefix +
                             "sample IDs in taxonomy file must be unique")

            self.assertEqual(
                sample_ids,
                expected_sample_ids,
                error_msg_prefix +
                "sample IDs in taxonomy file must match sample IDs in sample "
                "metadata file (having the same order is not required)")

            taxonomy_column = []
            for row in rows:
                self.assertEqual(len(row), len(header),
                                 error_msg_prefix +
                                 "each row must have the same number of cells "
                                 "as the header")
                taxonomy_column.append(row[0])

            taxonomy_ids = set(taxonomy_column)
            self.assertEqual(len(taxonomy_column), len(taxonomy_ids),
                             error_msg_prefix +
                             "taxonomy column values must be unique")

            for sample_id, column in zip(sample_ids, list(zip(*rows))[1:]):
                column = [float(value) for value in column]
                column_sum = sum(column)
                self.assertAlmostEqual(
                    column_sum,
                    1.0,
                    delta=0.001,
                    msg=error_msg_prefix +
                    "sample ID %r must have taxa frequencies that sum to 1.0, "
                    "not %r" % (sample_id, column_sum))

            return taxonomy_ids

    def _assert_valid_database_id_file(self, fp, expected_taxonomy_fp,
                                       expected_taxonomy_ids):
        error_msg_prefix = "Database identifiers file %r: " % fp

        with open(fp, newline='') as fh:
            rows = list(csv.reader(fh, delimiter='\t'))

            taxonomy_column = [row[0] for row in rows]
            taxonomy_ids = set(taxonomy_column)
            self.assertEqual(
                len(taxonomy_column),
                len(taxonomy_ids),
                error_msg_prefix + "taxonomy column values must be unique")

            self.assertEqual(
                taxonomy_ids,
                expected_taxonomy_ids,
                error_msg_prefix +
                "taxonomy column values must match taxonomy column values in "
                "%r (having the same order is not required)" %
                expected_taxonomy_fp)


if __name__ == '__main__':
    test_program = unittest.main(exit=False)

    if BAD_URLS:
        bad_urls_message = ['\nSome URLs could not be reached:']
        for fp, url in BAD_URLS:
            bad_urls_message.append('%s : %s' % (fp, url))
        sys.exit('\n'.join(bad_urls_message))

    if test_program.result.wasSuccessful():
        sys.exit(0)
    else:
        sys.exit(1)
