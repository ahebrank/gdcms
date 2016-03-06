"""
handle Google Docs (as in, for word processing)
"""

import lib.doc as doc
import re

def get_markup(gid):
  """
  collect the raw markup for a google doc id
  """
  url = "https://docs.google.com/feeds/download/documents/export/Export?id=%s&format=html" % gid
  return doc.url_fetch(url)

def insert_doc_content(tags, content, debug = False):
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

        with open(file, 'w') as fout:
          fout.write(html)
  