"""
interact with Google Sheets
"""

import json
import lib.doc as doc
import re

def collect_doc_ids(files):
  return doc.collect_doc_ids(files, 'gs')

def get_sheet_data(gid):
  """
  grab a json from the sheet
  """
  url = "https://spreadsheets.google.com/feeds/list/%s/od6/public/values?alt=json" % gid
  data = doc.url_fetch(url)
  if data is None:
    return None
  return field_hash(data)

def field_hash(data):
  """
  take the json dump and make a content -> [fields] maps
  """
  try:
    j = json.loads(data.decode('utf-8'))
    rows = j['feed']['entry']
  except Exception:
    return None

  fh = {}
  for r in rows:
    title = r['title']['$t']
    fields = {key.replace('gsx$', ''): r[key]['$t'] for key in r.keys() if key.startswith('gsx$')}
    fh[title] = fields

  return fh

def get_field_val(data, gid, content_id, field_id, default = 'Undefined'):
  """
  try to get a field value from the hash generated in field_hash
  """
  if gid in data:
    if content_id in data[gid]:
      if field_id in data[gid][content_id]:
        return data[gid][content_id][field_id]
  return default

def insert_sheet_content(tags, data, debug = False):
  """
  stick the structured data in the files
  """
  for gid in tags.keys():
    if not data[gid] is None:
      for file in tags[gid]:
        pat = r'(\{\{ *gs\:%s *\((.+),(.+)\) *\}\})' % (gid)
        regex = re.compile(pat)
        html = ''
        with open(file) as fin:
          html = fin.read()
        for match in regex.finditer(html):
          m = match.group(1).strip()
          content_id = match.group(2).strip()
          field_id = match.group(3).strip()

          insertion = get_field_val(data, gid, content_id, field_id)
          if debug:
            insertion = '<!-- insert from %s-->%s<!-- end insert from %s -->' % (gid, insertion, gid)
          html = html.replace(m, insertion)

        with open(file, 'w') as fout:
          fout.write(html)