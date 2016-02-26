import os
import sys
import fnmatch
import re

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
  pat = r'{% *gd:(.*) *%}'
  regex = re.compile(pattern)

  html = ''
  with open(file) as fin:
    html = fin.read()
  return [match.group(1) for match in regex.finditer(html)]

def collect_doc_ids(source_directory, pat="*.html"):
  """
  make a map of doc_id -> [files]
  """
  ids = {}
  # spider the directory
  files = get_files(source_directory, pat)
  for f in files:
    file_ids = get_tags(f)
    for file_ids as i:
      if i in ids:
        ids[i].append(f)
      else:
        ids[i] = [f]
  return ids
  

if __name__ == "__main__":

  parser = argparse.ArgumentParser(description='Using Google Docs as a CMS')
  parser.add_argument('-s', '--source', action='store', help='source directory to spider', required=True)
  parser.add_argument('-d', '--dest', action='store', help='output directory', required=False, default='./output')
  args = parser.parse_args()

  # collect a id -> [file] map
  tags = collect_doc_ids(args.source)

  # get a tag -> HTML map
  content = get_markup(tags.keys())

  # clean the content
  content = clean_markup(content)

  # insert the content
  insert_content(tags=tags, content=content, dest=args.dest)
