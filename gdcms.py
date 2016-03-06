#!/usr/bin/env python3

import os
import sys
import errno
import fnmatch
import re
import argparse
import urllib.request, urllib.error, urllib.parse

# local imports
import lib.cleaner as cleaner
import lib.sheets as sheets

debug = False

def get_files(src, pat):
  """
  recursively collect files
  """
  matches = []
  for root, dirnames, filenames in os.walk(src):
    for filename in fnmatch.filter(filenames, pat):
      matches.append(os.path.join(root, filename))
  return matches

def get_tags(file, tag_prefix):
  """
  return a list of GD IDs in file
  """
  pat = r'\{\{ *%s\:([\w\-_]+) *(\(.+\))* *\}\}' % (tag_prefix)
  regex = re.compile(pat)
  html = ''
  with open(file) as fin:
    html = fin.read()
  return [match.group(1).strip() for match in regex.finditer(html)]

def collect_doc_ids(source_directory, tag_prefix, pat="*.html"):
  """
  make a map of doc_id -> [files]
  """
  ids = {}
  # spider the directory
  files = get_files(source_directory, pat)
  for f in files:
    file_ids = get_tags(f, tag_prefix)
    for i in file_ids:
      if i in ids:
        ids[i].append(f)
      else:
        ids[i] = [f]
  return ids

def url_fetch(url):
  response = urllib.request.urlopen(url)
  resp_code = response.getcode()

  if (resp_code == 200):
    return response.read()
  return None

def get_markup(gid):
  """
  collect the raw markup for a google doc id
  """
  url = "https://docs.google.com/feeds/download/documents/export/Export?id=%s&format=html" % gid
  return url_fetch(url)

def get_sheet_data(gid):
  """
  grab a json from the sheet
  """
  url = "https://spreadsheets.google.com/feeds/list/%s/od6/public/values?alt=json" % gid
  data = url_fetch(url)
  if data is None:
    return None
  return sheets.field_hash(data)

def strip_src(file, src):
  return file.replace(src, '')

def get_dest_file(file, src, dest):
  """
  get the output file, make directories if needed
  """
  f = dest + strip_src(file, src)
  d = os.path.dirname(f)
  try:
    os.makedirs(d)
  except OSError as exception:
    if exception.errno != errno.EEXIST:
      raise
  return f

def insert_doc_content(tags, content, src, dest):
  """
  stick the markup in the files
  """
  for gid in tags.keys():
    if not content[gid] is None:
      insertion = "<!-- insert from %s -->\n%s\n<!-- end insert from %s -->" % (gid, content[gid], gid) if debug else content[gid]
      for file in tags[gid]:
        markup = content[gid]
        pat = r'(\{\{ *gd\:%s *\}\})' % (gid)
        regex = re.compile(pat)
        html = ''
        with open(file) as fin:
          html = fin.read()
        matches = [match.group(1).strip() for match in regex.finditer(html)]
        for m in matches:
          html = html.replace(m, insertion)

        dest_file = get_dest_file(file, src, dest)
        with open(dest_file, 'w') as fout:
          fout.write(html)

def insert_sheet_content(tags, data, src, dest):
  """
  stick the structured data in the files
  this must run after insert_doc_content
  """
  for gid in tags.keys():
    if not data[gid] is None:
      for src_file in tags[gid]:
        file = get_dest_file(src_file, src, dest)
        pat = r'(\{\{ *gs\:%s *\((.+),(.+)\) *\}\})' % (gid)
        regex = re.compile(pat)
        html = ''
        with open(file) as fin:
          html = fin.read()
        for match in regex.finditer(html):
          m = match.group(1).strip()
          content_id = match.group(2).strip()
          field_id = match.group(3).strip()

          insertion = sheets.get_field_val(data, gid, content_id, field_id)
          if debug:
            insertion = '<!-- insert from %s-->%s<!-- end insert from %s -->' % (gid, insertion, gid)

          html = html.replace(m, insertion)

        with open(file, 'w') as fout:
          fout.write(html)


if __name__ == "__main__":

  parser = argparse.ArgumentParser(description='Using Google Docs as a CMS')
  parser.add_argument('-s', '--source', action='store', help='source directory to spider', required=True)
  parser.add_argument('-d', '--dest', action='store', help='output directory', required=False, default='./output')
  parser.add_argument('-v', '--verbose', action='store_true', help='debug output', default=False)
  args = parser.parse_args()

  src = os.path.abspath(args.source)
  dest = os.path.abspath(args.dest)

  debug = args.verbose

  # collect a id -> [file] map
  doc_tags = collect_doc_ids(src, 'gd')
  sheet_tags = collect_doc_ids(src, 'gs')

  # get a tag -> content map
  doc_content = {gid: cleaner.clean(get_markup(gid)) for gid in doc_tags.keys()}
  sheet_data = {gid: get_sheet_data(gid) for gid in sheet_tags.keys()}

  # insert the content
  insert_doc_content(tags=doc_tags, content=doc_content, src=src, dest=dest)
  insert_sheet_content(tags=sheet_tags, data=sheet_data, src=src, dest=dest)
