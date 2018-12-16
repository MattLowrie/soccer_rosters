# -*- coding: utf-8 -*-
"""Collects data on D1 schools that have women's soccer programs.

Data is from Wikipedia and a Google search for current rosters.
Data is serialized to a local .csv file.
"""
# !pip install -q google
# !pip install -q wikitables

from googlesearch import search
from wikitables import import_tables

programs = import_tables("List of NCAA Division I women's soccer programs")

schools = {}
for program in programs[0].rows:
  columns = {}
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
    if found: break

print('Saving to file ...')
with open('d1_roster_urls.csv', 'w') as fw:
  # First write out column headers
  col_names = next(iter(schools.values()))
  fw.write(','.join(col_names.keys()) + '\n')
  for data in schools.values():
    fw.write(','.join(data.values()) + '\n')
