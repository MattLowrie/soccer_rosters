# -*- coding: utf-8 -*-
"""Collects data on D1 schools that have women's soccer programs.

Data is from Wikipedia and a Google search for current rosters.
Data is serialized to a local .csv file.
"""
# !pip install -q google
# !pip install -q wikitables

import argparse
import logging
from googlesearch import search
from wikitables import import_tables

def main():
  logger = logging.getLogger(__name__)

  # Get the list of schools from Wikipedia
  # https://en.wikipedia.org/wiki/List_of_NCAA_Division_I_women%27s_soccer_programs
  programs = import_tables("List of NCAA Division I women's soccer programs")

  schools = {}
  schools_filter = []
  if flags.schools:
    schools_filter = flags.schools.split(',')
    logger.debug('Only saving these schools: %s', str(schools_filter))
  for program in programs[0].rows:
    columns = {}
    if schools_filter and program['Institution'] not in schools_filter:
      continue
    for col_name in program.keys():
      cell_text = ''
      val = program[col_name].value
      # Ignore these schools since they aren't yet, or are soon leaving, D1.
      if (not val.startswith('California Baptist') and
          not val.startswith('LIU Brooklyn') and
          not val.startswith('North Alabama') and
          not val.startswith('New Orleans')):
        # Format the text of each table cell by removing non-ascii characters
        # and ignoring text after comment/formatting characters.
        for c in val:
          if c == '–': cell_text += '-'
          elif ord(c) > 128: cell_text += ' '
          elif c == '[': break
          elif c == '<': break
          else: cell_text += c
        clean_text = cell_text.strip()
        columns[col_name] = clean_text
    if 'Institution' in columns:
      schools[columns['Institution']] = columns
      logger.debug(columns)

  # for school in list(schools.keys())[:10]:
  for school in schools.keys():
    q = "%s 2018 women's soccer roster" % school
    for r in search(query=q, num=1, stop=10):
      found = False
      for expected_url_clue in ['roster.aspx', 'SportSelect', 'wsoc', 'w-soccer']:
        if expected_url_clue in r:
          schools[school]['Url'] = r
          found = True
          break
      if 'schedule.aspx' in r:
        schools[school]['Url'] = r.replace('schedule.aspx', 'roster.aspx')
        found = True
      if 'index.aspx' in r:
        schools[school]['Url'] = r.replace('index.aspx', 'roster.aspx')
        found = True
      if found: break

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
  parser.add_argument('--schools', metavar='"SCHOOL 1, SCHOOL 2, SCHOOL 3"',
                      help='A comma-separated list of schools to output.')
  flags = parser.parse_args()
  fmt = '%(asctime)s,%(msecs)-3d %(levelname)-8s %(filename)s - %(message)s'
  logging.basicConfig(level=logging.DEBUG,
                      format=fmt,
                      datefmt='%m-%d %H:%M:%S',
                      filename='/tmp/collect_roster_urls.log',
                      filemode='w')
  main()
