# -*- coding: utf-8 -*-
# Required: pip install wikitables

import logging
from wikitables import import_tables


def GetWomensSoccerArticleTable(schools_filter=None):
  """Specific function for importing and parsing the Wikipedia
  article on NCAA D1 Women's Soccer Programs.

  Returns:
    A dictionary of Wikipedia table data:
      key: A string of the school name. Example: "Stanford"
      value: A dictionary of table data. Example:
        {"Institution": "Stanford",
         "Location": "Palo Alto",
         "State": "California",
         "Type": "Private",
         "Nickname": "Cardinal",
         "Conference": "Pac-12"}
  """
  logger = logging.getLogger(__name__)

  # Get the list of schools from Wikipedia
  # https://en.wikipedia.org/wiki/List_of_NCAA_Division_I_women%27s_soccer_programs
  programs = import_tables("List of NCAA Division I women's soccer programs")

  schools = {}
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
  return schools
