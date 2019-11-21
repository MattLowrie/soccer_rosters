import argparse
import codecs
import logging
import os
import sys

from bs4 import BeautifulSoup as bs
from util import roster_file_util
import ncaa_roster_parser

LOGFILE = '/tmp/convert_roster_webpages_to_csv.log'
LOGGER = None


def read_webpages(webpage_dir, school_filter=None):
  """Collects the file content from the files in the specificed directory.

  Arguments:
    webpage_dir: A string of the directory to read from.
    school_filter: A list of schools to filter by. Only these schools will be
        output.

  Returns:
    A dict mapping the school name to its roster web page content:
        {<school name>: <roster webpage raw HTML content>}
  """
  webpages = {}
  webpage_files = os.listdir(webpage_dir)
  for webpage_file in webpage_files:
    # Get the school name from the file name. Convert underscores back into
    # spaces.
    school = webpage_file[:webpage_file.rfind('.')].replace('_', ' ')
    if school_filter and school not in school_filter:
      continue
    file_path = os.path.join(webpage_dir, webpage_file)
    content = roster_file_util.read_file(file_path)
    if webpage_file.endswith('webpage'):
      webpages[school] = content
  return webpages


def parse_webpages(webpages, schools, urls):
  """Selects an HTML processor for each school roster webpage.

  Arguments:
    webpages: A dict of strings of {school:webpage HTML} pairs.
    urls: A dict of strings of {school:url} pairs.

  Returns:
    A dict with a list of players for each school in the form of:
      {school 1: [{player 1 attributes},
                  {player 2 attributes}, ...
                  {player n attributes},],
       school 2: [{player 1 attributes},
                  {player 2 attributes}, ...
                  {player n attributes},], ...
      }
      Example:
        {'North Carolina': [{'name': 'Mia Hamm', 'position': 'F', ...},
                            {'name': ''}]}
  """
  school_teams = {}
  for school in webpages:
    LOGGER.debug('Processing {}...'.format(school))
    page = bs(webpages[school], 'html.parser')
    url = urls[schools.index(school)]
    if page:
      if 'roster.aspx' in url or 'womens-soccer/roster' in url:
        sidearm = ncaa_roster_parser.SidearmProcessor(page)
        school_teams[school] = sidearm.get_team()
      elif 'SportSelect' in url:
        sport_select_proc = ncaa_roster_parser.SportSelectProcessor(page)
        school_teams[school] = sport_select_proc.get_team()
      else:
        table_proc = ncaa_roster_parser.HtmlTableProcessor(page)
        school_teams[school] = table_proc.get_team()
    else:  # !page
      LOGGER.error('No webpage data for %s', school)
  return school_teams


def set_csv_rows(schools, locations, states, types, nicknames, conferences,
                 urls, teams):
  """Take all the collected data and put it in csv rows.

  Arguments:
    schools: A list of strings of school names.
    locations: A list of strings of school locations.
    states: A list of strings of school states.
    types: A list of strings of school types (e.g., 'Public', 'Private', etc.)
    nicknames: A list of strings of school nicknames.
    conferences: A list of strings of school conferences.
    urls: A dict of roster URLs with the school as the key.
    teams: A dict of each school's team. The dict values are lists of dicts of
        each player's attributes.

  Returns:
    A list of strings of each CSV row.
  """
  csv_rows = []
  for i, school in enumerate(schools):
    if school in teams:
      for player in teams[school]:
        csv_row = ','.join([
          school,
          locations[i],
          states[i],
          types[i],
          nicknames[i],
          conferences[i],
          urls[i],
        ])
        for k in player.keys():
          csv_row += ',' + player[k]
        csv_rows.append(csv_row)
  return csv_rows


def main():
  school_filter = []
  if flags.schools:
    school_filter = [f.strip() for f in flags.schools.split(',')]
    LOGGER.debug('Only processing these schools: %s', str(school_filter))

  schools, locations, states, types, nicknames, conferences, urls = \
      roster_file_util.read_school_info_file(flags.school_info_file,
                                             school_filter)

  webpages = read_webpages(flags.webpage_dir, school_filter)
  teams = parse_webpages(webpages, schools, urls)
  csv_rows = set_csv_rows(schools, locations, states, types, nicknames,
                          conferences, urls, teams)

  csv_header_row = ('School,City,State,Type,Nickname,Conference,Roster,Player,'
                    'Jersey,Position,Height,Hometown,Home State,High School,'
                    'Year,Club\n')
  with codecs.open(flags.output_file, 'w', 'utf-8-sig') as fw:
    fw.write(csv_header_row)
    for csv_row in csv_rows:
      fw.write(csv_row + '\n')


def _set_arguments():
  parser = argparse.ArgumentParser()
  parser.add_argument('--webpage_dir', metavar='DIRNAME',
                      default='roster_webpages',
                      help='Directory with webpage files to read in.')
  parser.add_argument('--school_info_file', metavar='FILENAME',
                      default='ncaa_d1_womens_soccer_programs.csv',
                      help='CSV file containing school data.')
  parser.add_argument('-o', '--output_file', metavar='FILENAME',
                      default='d1-rosters.csv',
                      help='The file to output CSV data into.')
  parser.add_argument('--schools', metavar='"SCHOOL 1,SCHOOL 2,SCHOOL 3"',
                      help='A comma-separated list of schools to output.')
  return parser.parse_args()


def _set_logger():
  fmt = '%(asctime)s,%(msecs)-3d %(levelname)-8s %(filename)s:%(lineno)d -> %(message)s'
  logging.basicConfig(level=logging.DEBUG,
                      format=fmt,
                      datefmt='%m-%d %H:%M:%S',
                      filename=LOGFILE,
                      filemode='w')
  return logging.getLogger(__name__)


if __name__ == '__main__':
  flags = _set_arguments()
  LOGGER = _set_logger()
  main()
