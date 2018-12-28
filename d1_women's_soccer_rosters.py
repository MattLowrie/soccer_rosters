# -*- coding: utf-8 -*-
"""D1 Women's Soccer Rosters.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1KfRuomeq8qA1eW__2lKL52J1L5OBswbU
"""
# !pip install -q beautifulsoup4
# !pip install -q google
# !pip install -q requests
# !pip install -q wikitables
# !pip install --upgrade certifi

import argparse
import codecs
import csv
import logging
import re
import requests
import time
import ncaa_roster_parser
import brotli
from bs4 import BeautifulSoup as bs
from googlesearch import search
from urllib.parse import urlparse
from urllib.parse import urlunparse
from wikitables import import_tables
import sys

def main():
  logger = logging.getLogger(__name__)
  logger.setLevel(logging.DEBUG)
  school_filter = []
  if flags.schools:
    school_filter = [f.strip() for f in flags.schools.split(',')]
  # d1_roster_urls.csv headers:
  roster_headers = ['Institution', 'Location', 'State', 'Type', 'Nickname', 'Conference', 'Url']
  schools = []
  locations = []
  states = []
  types = []
  nicknames = []
  conferences = []
  urls = []
  with open('ncaa_d1_womens_soccer_programs.csv', 'r') as rosters_csv:
    reader = csv.DictReader(rosters_csv)
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
  print(schools)

  http_headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9'
  }

  request_args = []
  corrected_urls = []
  for i, url in enumerate(urls):
    parsed_url = urlparse(url)
    params = {}
    if parsed_url.query:
      query_params = parsed_url.query.split('&')
      for query_param in query_params:
        if '=' in query_param:
          k, v = query_param.split('=')
          # SidearmSports sites use the path= query param to designate the
          # sport to display. For women's soccer, the value of this param can
          # be wsoc, wsoccer, soc, or <empty string>. Since the Google results
          # can potentially provide the link to the wrong sport, we verify that
          # the path= value will pull up the women's soccer roster.
          if k == 'path' and v:
            # If the param is 'path' and the value is NOT empty string ...
            if 'soc' not in v:
              # ... and the value doesn't contain 'soc', set the param value to
              # which should work in all cases.
              params[k] = 'wsoc'
            else:
              params[k] = v
          else:
            params[k] = v
        else:
          params[query_param] = None
    reconstituted_url = urlunparse((
      parsed_url.scheme,
      parsed_url.netloc,
      parsed_url.path,
      None, None, None))
    request_args.append({
        'url': reconstituted_url,
        'params': params,
        'headers': http_headers,
    })
    corrected_url = reconstituted_url + '?'
    corrected_url += '&'.join(['%s=%s' % (k, v) for k, v in params.items()])
    corrected_urls.append(corrected_url)

  # index_start = 200
  # index_end = 250
  # test_set = request_args[index_start:index_end]
  # for tester in test_set:
  #   print(tester['url'])

  # print(len(corrected_urls))
  # print(len(urls))
  soups = []
  for i, req_args in enumerate(request_args):
  # for req_args in test_set:
    try:
      r = requests.get(**req_args)
      if r.status_code == 200:
        if ('Content-encoding' in r.headers and
            r.headers['Content-Encoding'] == 'br'):
          soups.append(bs(brotli.decompress(r.content), 'html.parser'))
        else:
          soups.append(bs(r.content, 'html.parser'))
      else:
        soups.append('')
        logger.warn('Request args')
        logger.warn(req_args)
        logger.warn('Status code %d for %s', r.status_code, corrected_urls[i])
        logger.warn('HTTP reason: %s', r.reason)
        logger.warn('HTTP response headers:')
        logger.warn(r.raw.getheaders())
    except requests.exceptions.ConnectionError:
      logger.error('Connection error for: %s', req_args['url'])
      soups.append('')


  teams = []
  for i, soup in enumerate(soups):
  # for offset, soup in enumerate(soups):
    # i = index_start + offset
    logger.debug('=' * 20)
    logger.debug(urls[i])
    if 'roster.aspx' in urls[i] and soup:
      sidearm = ncaa_roster_parser.SidearmProcessor(soup)
      teams.append(sidearm.GetTeam())
    elif '2018-19/roster' in urls[i] and soup:
      table_proc = ncaa_roster_parser.TableProcessor(soup)
      teams.append(table_proc.GetTeam())
    elif 'SportSelect' in urls[i] and soup:
      table_proc = ncaa_roster_parser.SportSelectProcessor(soup)
      teams.append(table_proc.GetTeam())
    else:
      logger.warn('Site processor not found: %s', urls[i])
      teams.append({})

  csv_rows = []
  for i, team in enumerate(teams):
  # for offset, team in enumerate(teams):
    # i = index_start + offset
    for player in team:
      csv_row = ','.join([
        schools[i],
        locations[i],
        states[i],
        types[i],
        nicknames[i],
        conferences[i],
        corrected_urls[i],
      ])
      if isinstance(player, str):
        csv_row =+ player
      elif isinstance(player, dict):
        for k in player.keys():
          csv_row += ',' + player[k]
      csv_rows.append(csv_row)

  with codecs.open(flags.output_file, 'w', 'utf-8-sig') as fw:
    fw.write('School,City,State,Type,Nickname,Conference,Roster,Player,Jersey,Position,Height,Hometown,Home State,High School,Year,Club\n')
    for csv_row in csv_rows:
      fw.write(csv_row + '\n')


if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('-o', '--output_file', metavar='FILENAME',
                      default='rosters-out.csv',
                      help='The filename to output the csv data.')
  parser.add_argument('--schools', metavar='"SCHOOL 1, SCHOOL 2, SCHOOL 3"',
                      help='A comma-separated list of schools to output.')
  flags = parser.parse_args()
  fmt = '%(asctime)s,%(msecs)-3d %(levelname)-8s %(filename)s %(name)s - %(message)s'
  f = logging.Formatter(fmt=fmt, datefmt='%m-%d %H:%M:%S')
  h = logging.FileHandler('/tmp/d1_rosters.log', 'w', encoding='UTF-8')
  h.setFormatter(f)
  h.setLevel(logging.DEBUG)
  logging.basicConfig(handlers=[h])
  main()
