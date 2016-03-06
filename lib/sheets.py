import json

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