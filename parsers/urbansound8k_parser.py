#!/usr/bin/env python
# CREATED: 4/21/16 1:59 PM by Justin Salamon <justin.salamon@nyu.edu>
"""
Translates the UrbanSound8K metadata file UrbanSound8K.csv to a set
of JAMS files - one file per each of the 8732 clips in the dataset.

The original data is found online at the following URL:
    https://serv.cusp.nyu.edu/projects/urbansounddataset/

To parse the entire dataset, you need to provide the path to the
metadata.csv file.
Example:
./urbansound8k_parser.py ~/UrbanSound8K/metadata/UrbanSound8K.csv -o ~/UrbanSound8K_jams/
"""

__author__ = "J. Salamon"
__copyright__ = "Copyright 2016, Justin Salamon"
__license__ = "GPL"
__version__ = "1.0"
__email__ = "justin.salamon@nyu.edu"

import argparse
import logging
import os
import time
import pandas as pd
import jams


def create_snippet_jam(row):

    # Create jam
    jam = jams.JAMS()

    # Create annotation
    ann = jams.Annotation('tag_open')

    # Add tag with snippet sound class
    ann.append(time=0,
               duration=row['end'] - row['start'],
               value=row['class'],
               confidence=1.)
    ann.duration = row['end'] - row['start']

    # Fill file metadata
    fill_file_metadata(jam, row)

    # Fill annotation metadata
    fill_annotation_metadata(ann, row)

    # Add annotation to jam
    jam.annotations.append(ann)

    # Return jam
    return jam


def fill_file_metadata(jam, row):
    """Fills the global metada into the JAMS jam."""
    jam.file_metadata.title = row['slice_file_name']
    jam.file_metadata.release = '1.0'
    jam.file_metadata.duration = row['end'] - row['start']
    jam.file_metadata.artist = 'UrbanSound8K'


def fill_annotation_metadata(ann, row):
    """Fills the annotation metadata."""
    ann.annotation_metadata.annotation_tools = 'Sonic Visualiser'
    ann.annotation_metadata.curator = (
        jams.Curator(name='Justin Salamon', email='justin.salamon@nyu.edu'))

    annotators = {'annotators': [
        {'name': 'Justin Salamon', 'email': 'justin.salamon@nyu.edu'},
        {'name': 'Christopher Jacoby', 'email': 'christopher.jacoby@gmail.com'}
        ]}
    ann.annotation_metadata.annotator = jams.Sandbox(**annotators)

    ann.annotation_metadata.version = '1.0'
    ann.annotation_metadata.corpus = 'UrbanSound8K'
    ann.annotation_metadata.annotation_rules = (
        'See: J. Salamon, C. Jacoby and J. P. Bello, "A Dataset and Taxonomy '
        'for Urban Sound Research", in Proc. 22nd ACM International Conference '
        'on Multimedia, Orlando, USA, Nov. 2014.')
    ann.annotation_metadata.data_source = (
        'https://serv.cusp.nyu.edu/projects/urbansounddataset/')
    ann.annotation_metadata.validation = ''

    # Store all metadata in sandbox too
    ann.sandbox.update(**row)


def process_metadata(metadata_file, out_dir):
    """Converts the UrbanSound8K metadata file UrbanSound8K.csv to a set
    of JAMS files - one file per each of the 8732 clips in the dataset."""

    # Load metadata file
    df = pd.read_csv(metadata_file)

    # Each row represents a single clip
    for idx, row in df.iterrows():

        # Create snippet JAMS with everything filled in
        jam = create_snippet_jam(row)

        # Save JAMS
        out_file = os.path.join(
            out_dir, row['slice_file_name'].replace(".wav", ".jams"))
        jam.save(out_file)


def main():
    """Main function to convert the dataset into JAMS."""
    parser = argparse.ArgumentParser(
        description="Converts the UrbanSound8K metadata file UrbanSound8K.csv"
                    " to the JAMS format (one JAMS file per sound clip).",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("metadata_file",
                        action="store",
                        help="Path to UrbanSound8K.csv")
    parser.add_argument("-o",
                        action="store",
                        dest="out_dir",
                        default="UrbanSound8K_jams",
                        help="Output JAMS folder")
    args = parser.parse_args()
    start_time = time.time()

    # Setup the logger
    logging.basicConfig(format='%(asctime)s: %(message)s', level=logging.INFO)

    # Run the parser
    process_metadata(args.metadata_file, args.out_dir)

    # Done!
    logging.info("Done! Took %.2f seconds.", time.time() - start_time)

if __name__ == '__main__':
    main()