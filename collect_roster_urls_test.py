# -*- coding: utf-8 -*-
"""Tests for the collect_roster_urls module.

The parameterized module is required:
pip install -q parameterized
"""
from collections import namedtuple
from parameterized import parameterized
import unittest
from unittest.mock import patch

import collect_roster_urls

WikiData = namedtuple('WikiData', ['value'])

class CollectRosterUrlsTest(unittest.TestCase):

  @parameterized.expand([
    ('Kansas City[b]', 'Kansas City'),
    ('Loyola–Chicago', 'Loyola-Chicago'),
    ('UCLA æ', 'UCLA')
  ])
  def test_clean_text(self, input, expected):
    actual = collect_roster_urls._clean_text(input)
    self.assertEqual(expected, actual)

  # Test data for test_parse_school_data
  test1_programs = [{'Institution': WikiData('Alabama A&M'),
                     'Location':    WikiData('Normal'),
                     'State':       WikiData('Alabama'),
                     'Type':        WikiData('Public'),
                     'Nickname':    WikiData('Bulldogs'),
                     'Conference':  WikiData('SWAC')},
                    {'Institution': WikiData('Arkansas–Pine Bluff'),
                     'Location':    WikiData('Pine Bluff'),
                     'State':       WikiData('Arkansas'),
                     'Type':        WikiData('Public'),
                     'Nickname':    WikiData('Golden Lady Lions'),
                     'Conference':  WikiData('SWAC')}]
  test1_filter = []
  test1_expected = {'Alabama A&M':         {'Institution': 'Alabama A&M',
                                            'Location':    'Normal',
                                            'State':       'Alabama',
                                            'Type':        'Public',
                                            'Nickname':    'Bulldogs',
                                            'Conference':  'SWAC'},
                    'Arkansas-Pine Bluff': {'Institution': 'Arkansas-Pine Bluff',
                                            'Location':    'Pine Bluff',
                                            'State':       'Arkansas',
                                            'Type':        'Public',
                                            'Nickname':    'Golden Lady Lions',
                                            'Conference':  'SWAC'}}
  test2_programs = [{'Institution': WikiData('BYU'),
                     'Location':    WikiData('Provo'),
                     'State':       WikiData('Utah')},
                    {'Institution': WikiData('LIU[c]'),
                     'Location':    WikiData('Brookville[d]'),
                     'State':       WikiData('New York')},
                    {'Institution': WikiData('Louisiana–Monroe'),
                     'Location':    WikiData('Monroe'),
                     'State':       WikiData('Louisiana')}]
  test2_filter = ['LIU']
  test2_expected = {'LIU': {'Institution': 'LIU',
                            'Location':    'Brookville',
                            'State':       'New York'}}
  test3_programs = [{'School': WikiData('Hard Knocks')}]
  test3_filter = []
  test3_expected = {}
  @parameterized.expand([
    (test1_programs, test1_filter, test1_expected),
    (test2_programs, test2_filter, test2_expected),
    (test3_programs, test3_filter, test3_expected),
  ])
  def test_parse_school_data(self, programs, filter, expected):
    actual = collect_roster_urls._parse_school_data(programs, filter)
    self.assertEqual(expected, actual)

  # Test 1 processing multiple urls
  searchtest1_in = {'Pepperdine': {'Institution': 'Pepperdine',
                                   'Conference':  'West Coast'},
                    'TCU':        {'Institution': 'TCU',
                                   'State':       'Texas'},
                    'UCF':        {'Institution': 'UCF',
                                   'Nickname':    'Knights'},
                    'Virginia':   {'Institution': 'Virginia',
                                   'Type':        'Public'}}
  searchtest1_ex = {'Pepperdine': {'Institution': 'Pepperdine',
                                   'Conference':  'West Coast',
                                   'Url':         'https://pep.team/SportSelect.html'},
                    'TCU':        {'Institution': 'TCU',
                                   'State':       'Texas',
                                   'Url':         'https://tcu.frogs/wsoc/team.html'},
                    'UCF':        {'Institution': 'UCF',
                                   'Nickname':    'Knights',
                                   'Url':         'https://goknights.edu/roster.aspx?path=wsoccer'},
                    'Virginia':   {'Institution': 'Virginia',
                                   'Type':        'Public',
                                   'Url':         'https://v/wsoc/roster.aspx?path=wsoc'}}
  searchtest1_ret = [
    # Mock search result for Pepperdine
    ['https://pep.team/SportSelect.html'],
    # Mock search results (2) for TCU
    ['https://tcu.frogs/wbball/team.html',
     'https://tcu.frogs/wsoc/team.html'],
    # Mock search results for UCF
    ['https://goknights.edu/schedule.aspx?schedule=123&path=wsoccer'],
    # Mock search results for Virginia
    ['https://v/wsoc/roster.aspx?roster=123&path=bball']]
  searchtest1_esc = 4
  searchtest1_elc = 0
  # Test 2 verify logging
  searchtest2_in = {'Nowhere school': {'Institution': 'nowhere'}}
  searchtest2_ex = {'Nowhere school': {'Institution': 'nowhere'}}
  searchtest2_ret = [['https://nowhere.edu/nosports.html']]
  searchtest2_esc = 1
  searchtest2_elc = 1
  # Test 3 remove year
  searchtest3_in = {'IUPUI':              {'Institution': 'IUPUI',
                                           'Location': 'Indianapolis'},
                    'Louisville':         {'Institution': 'Louisville',
                                           'Location': 'Kentucky'},
                    'Jacksonville State': {'Intitution': 'Jacksonville State',
                                           'Nickname': 'Gamecocks'}}
  searchtest3_ex = {'IUPUI':              {'Institution': 'IUPUI',
                                           'Location': 'Indianapolis',
                                           'Url': 'https://iupuijags.com/sports/womens-soccer/roster'},
                    'Louisville':         {'Institution': 'Louisville',
                                           'Location': 'Kentucky',
                                           'Url': 'https://gocards.com/sports/womens-soccer/roster'},
                    'Jacksonville State': {'Intitution': 'Jacksonville State',
                                           'Nickname': 'Gamecocks',
                                           'Url': 'https://jsugamecocksports.com/sports/womens-soccer/roster'}}

  searchtest3_ret = [
    # Mock search result for IUPUI
    ['https://iupuijags.com/sports/womens-soccer/roster/2019-2020'],
    # Mock search result for Louisville
    ['https://gocards.com/sports/womens-soccer/roster/2018'],
    # Mock search result for Jacksonville State
    ['https://jsugamecocksports.com/sports/womens-soccer/roster/2018-19'],
  ]
  searchtest3_esc = 3
  searchtest3_elc = 0
  @parameterized.expand([
    (searchtest1_in, searchtest1_ex, searchtest1_ret, searchtest1_esc, searchtest1_elc),
    (searchtest2_in, searchtest2_ex, searchtest2_ret, searchtest2_esc, searchtest2_elc),
    (searchtest3_in, searchtest3_ex, searchtest3_ret, searchtest3_esc, searchtest3_elc),
  ])
  @patch('collect_roster_urls.search')
  @patch('collect_roster_urls.LOGGER')
  def test_search_for_roster_urls(self, input, expected, mock_search_result,
                                  expected_search_count, expected_logger_count,
                                  mock_logger, mock_search):
    mock_search.side_effect = mock_search_result
    collect_roster_urls._search_for_roster_urls(input)
    self.maxDiff = None  # This expands the diff output for test failures
    self.assertEqual(expected, input)
    self.assertEqual(expected_search_count, mock_search.call_count)
    self.assertEqual(expected_logger_count, mock_logger.warning.call_count)


  @parameterized.expand([
    ('https://school.edu/roster.aspx?roster=432&path=wsoc',
     'https://school.edu/roster.aspx?path=wsoc'),
    ('http://google.com',
     'http://google.com'),
  ])
  def test_standardize_url(self, input, expected):
    actual = collect_roster_urls._standardize_url(input)
    self.assertEqual(expected, actual)


if __name__ == '__main__':
  unittest.main()