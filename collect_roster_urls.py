# -*- coding: utf-8 -*-
"""Collects data about D1 colleges that have women's soccer programs.

Data is collected from Wikipedia and a Google search for current rosters.
Data is saved to a local .csv file.

These modules are required:
pip install --user google
pip install --user wikitables
"""

import argparse
from googlesearch import search
import logging
import re
from urllib.parse import urlparse, urlunparse, parse_qs
from wikitables import import_tables

LOGFILE = '/tmp/collect_roster_urls.log'
LOGGER = None


def _clean_text(text):
  """Cleans raw text from the Wikipedia table.

  Replaces any non-ASCII character with a space.
  Converts em dashes to regular dash.
  Removes all bracketed text, like footnote links (e.g, [a])
  
  Args:
    text: A string of the text to clean.
  
  Returns:
    A string of the clean text.
  """
  # Format the text of each table cell by removing non-ascii characters
  # and ignoring text after comment/formatting characters.
  clean_text = ''
  open_bracket = False
  for c in text:
    if c in '>]}': open_bracket = False
    elif open_bracket: continue
    elif c in '{[<': open_bracket = True
    elif c == '–': clean_text += '-'
    elif ord(c) > 128: clean_text += ' '
    else: clean_text += c
  clean_text = clean_text.strip()
  return clean_text


def _parse_school_data(programs, schools_filter):
  """Converts a list of wiki table rows into a dict.

  Args:
    programs: A list of wiki table rows.
    schools_filter: A list of school names. If provided, only the school names
        in the filter list are returned.

  Returns:
    A dict in the form of:
      Key: The school name.
      Value: A dict of attributes about the school. Each wiki table column
          is the key of this dict.
  """
  schools = {}
  for program in programs:
    if 'Institution' in program:
      school_name = _clean_text(program['Institution'].value)
      rowData = {}
      if schools_filter and school_name not in schools_filter:
        # Skip if not in the filter
        continue
      for col_name in program.keys():
        rowData[col_name] = _clean_text(program[col_name].value)
      schools[rowData['Institution']] = rowData
  return schools


def _standardize_url(url):
  """Removes extranious data from the url and standardizes the format."""
  if any([p in url for p in ['roster.aspx', 'index.aspx', 'schedule.aspx']]):
    parts = urlparse(url)
    params = parse_qs(parts.query)
    qs = None
    # Only save the path= query string
    if 'path' in params:
      # The dict value is a list, so search all values in the list
      val = [v for v in params['path'] if 'soc' in v]
      if val:
        qs = 'path={}'.format(val[0])
      else:
        # If a different sport was collected in the url, change it to wsoc
        qs = 'path=wsoc'
    path = parts.path.replace('index', 'roster')
    path = parts.path.replace('schedule', 'roster')
    url = urlunparse((parts.scheme, parts.netloc, path, None, qs, None))
  # Remove any year specification, e.g., 2019-2020 at the end of a url. The
  # default /roster path will navigate to the current year.
  url = re.sub(r'roster\/\d{2,4}-*\d{0,4}$', 'roster', url)
  return url


def _search_for_roster_urls(schools):
  """Searches Google for the roster URL of each school.

  Modifies the input dict by adding a 'Url' field.

  Args:
    schools: A dict of school data.
  """
  for school in schools.keys():
    q = "{} women's soccer roster".format(school)
    for url in search(query=q, num=1, stop=10):
      if any([s in url for s in ['roster.aspx', 'SportSelect', 'wsoc',
                                 'w-soccer', 'womens-soccer']]):
        schools[school]['Url'] = _standardize_url(url)
        break
    if 'Url' not in schools[school]:
      LOGGER.warning('No roster url found for {}'.format(school))


def main():
  schools_filter = []
  if flags.schools:
    schools_filter = flags.schools.split(',')
    LOGGER.debug('Only saving these schools: {}'.format(str(schools_filter)))

  # Get the list of schools from Wikipedia
  # https://en.wikipedia.org/wiki/List_of_NCAA_Division_I_women%27s_soccer_programs
  wikiTables = import_tables("List of NCAA Division I women's soccer programs")

  schools = _parse_school_data(wikiTables[0].rows, schools_filter)
  _search_for_roster_urls(schools)

  # Write data in CSV format
  with open(flags.output_file, 'w') as fw:
    # First write out column headers
    col_names = next(iter(schools.values()))
    fw.write(','.join(col_names.keys()) + '\n')
    for data in schools.values():
      fw.write(','.join(data.values()) + '\n')


if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('-o', '--output_file', metavar='FILENAME',
                      default='ncaa_d1_womens_soccer_programs.csv',
                      help='The filename to output the csv data.')
  parser.add_argument('--schools', metavar='SCHOOL 1,SCHOOL 2,SCHOOL 3',
                      help='A comma-separated list of schools to output.')
  flags = parser.parse_args()
  fmt = '%(asctime)s,%(msecs)-3d %(levelname)-8s %(filename)s:%(lineno)d -> %(message)s'
  logging.basicConfig(level=logging.DEBUG,
                      format=fmt,
                      datefmt='%m-%d %H:%M:%S',
                      filename=LOGFILE,
                      filemode='w')
  LOGGER = logging.getLogger(__name__)
  main()
