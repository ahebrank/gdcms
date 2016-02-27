import os
import sys
import fnmatch
import re
import argparse
import urllib2
from lib.cleaner import clean
import errno

def get_files(src, pat):
  """
  recursively collect files
  """
  matches = []
  for root, dirnames, filenames in os.walk(src):
    for filename in fnmatch.filter(filenames, pat):
      matches.append(os.path.join(root, filename))
  return matches

def get_tags(file):
  """
  return a list of GD IDs in file
  """
  ids = []
  pat = r'\{\{ *gd\:(.*) *\}\}'
  regex = re.compile(pat)
  html = ''
  with open(file) as fin:
    html = fin.read()
  return [match.group(1).strip() for match in regex.finditer(html)]

def collect_doc_ids(source_directory, pat="*.html"):
  """
  make a map of doc_id -> [files]
  """
  ids = {}
  # spider the directory
  files = get_files(source_directory, pat)
  for f in files:
    file_ids = get_tags(f)
    for i in file_ids:
      if i in ids:
        ids[i].append(f)
      else:
        ids[i] = [f]
  return ids

def get_markup(gid):
  """
  collect the raw markup for a google doc id
  """
  url = "https://docs.google.com/feeds/download/documents/export/Export?id=%s&format=html" % gid
  response = urllib2.urlopen(url)
  resp_code = response.getcode()

  if (resp_code == 200):
    return response.read()
  return None

def get_dest_file(file, src, dest):
  """
  get the output file, make directories if needed
  """
  f = dest + file.replace(src, '')
  d = os.path.dirname(f)
  try:
    os.makedirs(d)
  except OSError as exception:
    if exception.errno != errno.EEXIST:
      raise
  return f

def insert_content(tags, content, src, dest):
  """
  stick the markup in the files
  """
  for gid in tags.keys():
    if not content[gid] is None:
      for file in tags[gid]:
        markup = content[gid]
        pat = r'(\{\{ *gd\:' + gid + ' *\}\})'
        regex = re.compile(pat)
        html = ''
        with open(file) as fin:
          html = fin.read()
        matches = [match.group(1).strip() for match in regex.finditer(html)]
        for m in matches:
          html = html.replace(m, content[gid])

        dest_file = get_dest_file(file, src, dest)
        with open(dest_file, 'w') as fout:
          fout.write(html)


if __name__ == "__main__":

  parser = argparse.ArgumentParser(description='Using Google Docs as a CMS')
  parser.add_argument('-s', '--source', action='store', help='source directory to spider', required=True)
  parser.add_argument('-d', '--dest', action='store', help='output directory', required=False, default='./output')
  args = parser.parse_args()

  src = os.path.abspath(args.source)
  dest = os.path.abspath(args.dest)

  # collect a id -> [file] map
  tags = collect_doc_ids(src)

  # get a tag -> HTML map
  content = {gid: clean(get_markup(gid)) for gid in tags.keys()}

  # insert the content
  insert_content(tags=tags, content=content, src=src, dest=dest)
