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
                                   'Url':         'https://goknights.edu/roster.aspx'},
                    'Virginia':   {'Institution': 'Virginia',
                                   'Type':        'Public',
                                   'Url':         'https://v/wsoc/roster.aspx'}}
  searchtest1_ret = [['https://pep.team/SportSelect.html'],
                     ['https://tcu.frogs/wbball/team.html',
                      'https://tcu.frogs/wsoc/team.html'],
                     ['https://goknights.edu/schedule.aspx'],
                     ['https://v/wsoc/index.aspx']]
  searchtest1_ecc = 4
  @parameterized.expand([
    (searchtest1_in, searchtest1_ex, searchtest1_ret, searchtest1_ecc)
  ])
  @patch('collect_roster_urls.search')
  def test_search_for_roster_urls(self, input, expected, mock_search_result,
                                  expected_call_count, mock_search):
    mock_search.side_effect = mock_search_result
    collect_roster_urls._search_for_roster_urls(input)
    self.maxDiff = None  # This expands the diff output for test failures
    self.assertEqual(expected, input)
    self.assertEqual(expected_call_count, mock_search.call_count)


if __name__ == '__main__':
  unittest.main()