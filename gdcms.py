#!/usr/bin/env python3

import os
import sys
import argparse

# local imports
import lib.files as files
import lib.doc as doc
import lib.pages as pages
import lib.sheets as sheets

if __name__ == "__main__":

  parser = argparse.ArgumentParser(description='Using Google Docs as a CMS')
  parser.add_argument('-s', '--source', action='store', help='source directory to spider', required=True)
  parser.add_argument('-d', '--dest', action='store', help='output directory', required=False, default='./output')
  parser.add_argument('-v', '--verbose', action='store_true', help='debug output', default=False)
  args = parser.parse_args()

  src = os.path.abspath(args.source)
  dest = os.path.abspath(args.dest)

  debug = args.verbose

  # copy over the files
  files = files.copy_files(src, dest)

  # collect id -> [file] maps for the tag variations
  doc_tags = pages.collect_doc_ids(files)
  sheet_tags = sheets.collect_doc_ids(files)

  # get a tag -> content map for each tag variation
  doc_content = {gid: pages.get_clean_markup(gid) for gid in doc_tags.keys()}
  sheet_data = {gid: sheets.get_sheet_data(gid) for gid in sheet_tags.keys()}

  # insert the content for each document type
  pages.insert_doc_content(doc_tags, doc_content, debug)
  sheets.insert_sheet_content(sheet_tags, sheet_data, debug)
