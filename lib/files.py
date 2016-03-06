"""
file handling utilities
"""

import os
import shutil
import fnmatch
import errno

def strip_src(file, src):
  """ 
  remove the src path from a filename
  """
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

def copy_file_to_dest(file, src, dest):
  """
  copy a file from src to dest, return the dest filename
  """
  target = get_dest_file(file, src, dest)
  shutil.copyfile(file, target)
  return target

def get_files(src, pat):
  """
  recursively collect files
  """
  matches = []
  for root, dirnames, filenames in os.walk(src):
    for filename in fnmatch.filter(filenames, pat):
      matches.append(os.path.join(root, filename))
  return matches

def copy_files(src, dest, pat="*.html"):
  """
  copy over files from src to dest
  """
  files = get_files(src, pat)
  return [copy_file_to_dest(f, src, dest) for f in files]