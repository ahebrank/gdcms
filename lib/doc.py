"""
general Google Doc functions
"""

import urllib.request, urllib.error, urllib.parse
import re

def url_fetch(url):
  """
  wrap urllib to get a URL
  """
  try:
    response = urllib.request.urlopen(url)
    resp_code = response.getcode()
  except:
    return None

  if (resp_code == 200):
    return response.read()
  return None

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

def collect_doc_ids(files, tag_prefix):
  """
  make a map of doc_id -> [files]
  """
  ids = {}
  for f in files:
    file_ids = get_tags(f, tag_prefix)
    for i in file_ids:
      if i in ids:
        ids[i].append(f)
      else:
        ids[i] = [f]
  return ids