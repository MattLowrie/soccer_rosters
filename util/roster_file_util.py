"""Utility for file operations."""
import csv
import os

def read_school_info_file(file_name, school_filter=None):
  """Parses a CSV file containing school infomration.

  The school information in the CSV file should be parsed from the Wikipedia
  page about women's D1 soccer programs:
  https://en.wikipedia.org/wiki/List_of_NCAA_Division_I_women%27s_soccer_programs

  This function expects the columns: 'Institution', 'Location', 'State', 'Type',
  'Nickname', 'Conference' as well as, 'Url' for the roster webpage.

  Arguments:
    file_name: A string of the file name to read from.
    school_filter: A list of school names as strings to filter out of the file.
        Only schools in the filter list will be returned.

  Return values:
    A tuple of lists, one list for each CVS column, each of the same length
    equal to the number of CSV rows.
  """
  schools = []
  locations = []
  states = []
  types = []
  nicknames = []
  conferences = []
  urls = []
  with open(file_name, 'r') as school_info_csv:
    reader = csv.DictReader(school_info_csv)
    for row in reader:
      if school_filter and row['Institution'] not in school_filter:
        continue
      schools.append(row['Institution'])
      locations.append(row['Location'])
      states.append(row['State'])
      types.append(row['Type'])
      nicknames.append(row['Nickname'])
      conferences.append(row['Conference'])
      urls.append(row['Url'])
  return schools, locations, states, types, nicknames, conferences, urls


def read_file(file_path):
  """Reads and returns the contents of the specificed file.

  Arguments:
    file_path: A string of the file to open.

  Returns:
    A string of the file contents.
  """
  with open(file_path, 'r', encoding='utf-8') as fo:
    return fo.read()


def write_file(file_name, content, dir_path=None):
  """Saves content into specificed file. Creates sub-directories if needed.

  Arguments:
    file_name: A string of the file name to write into.
    content: A string of the file content to write.
    dir_path: An optional string of a sub-directory path to save the file in.
  """
  full_path = ''
  if dir_path:
    os.makedirs(dir_path, exist_ok=True)
    full_path = dir_path
  save_path = os.path.join(full_path, file_name)
  with open(save_path, 'w', encoding='utf-8') as fw:
    fw.write(content)
