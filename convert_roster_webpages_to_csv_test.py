"""Unit tests for convert_roster_webpages_to_csv.py"""
import unittest
from unittest import mock

import convert_roster_webpages_to_csv


class ConvertRosterWebpagesToCsvTest(unittest.TestCase):

  @mock.patch('convert_roster_webpages_to_csv.os')
  @mock.patch('convert_roster_webpages_to_csv.roster_file_util')
  def test_read_webpages(self, mock_fu, mock_os):
    fake_files = ['school_1.url', 'school_1.webpage',
                  'school_2.url', 'school_2.webpage']
    mock_os.listdir.return_value = fake_files
    mock_os.path.join.side_effect = ['fake_path_1', 'fake_path_2',
                                     'fake_path_3', 'fake_path_4']
    fake_content = ['http://page1', '<html page 1>',
                    'http://page2', '<html page 2>']
    mock_fu.read_file.side_effect = fake_content
    actual_webpages, actual_urls = \
        convert_roster_webpages_to_csv.read_webpages('fake_dir')
    expected_webpages = {
      'school 1': fake_content[1],
      'school 2': fake_content[3],
    }
    expected_urls = {
      'school 1': fake_content[0],
      'school 2': fake_content[2],
    }
    self.assertEqual(expected_webpages, actual_webpages)
    self.assertEqual(expected_urls, actual_urls)

  @mock.patch('convert_roster_webpages_to_csv.bs')
  @mock.patch('convert_roster_webpages_to_csv.ncaa_roster_parser')
  def test_parse_webpages(self, mock_nrp, mock_bs):
    team_a = [{'name': 'player a'}, {'name': 'player b'}, {'name': 'player c'}]
    team_b = [{'name': 'player m'}, {'name': 'player n'}, {'name': 'player o'}]
    team_c = [{'name': 'player x'}, {'name': 'player y'}, {'name': 'player z'}]
    mock_sidearm = mock.MagicMock()
    mock_table = mock.MagicMock()
    mock_sport_select = mock.MagicMock()
    mock_nrp.SidearmProcessor.return_value = mock_sidearm
    mock_nrp.HtmlTableProcessor.return_value = mock_table
    mock_nrp.SportSelectProcessor.return_value = mock_sport_select
    mock_sidearm.get_team.return_value = team_a
    mock_table.get_team.return_value = team_b
    mock_sport_select.get_team.return_value = team_c
    fake_webpages = {
      'school 1': '<html page 1>',
      'school 2': '<html page 2>',
      'school 3': '<html page 3>',
    }
    fake_urls = {
      'school 1': 'http://page1/roster.aspx',
      'school 2': 'http://page2/2018-19/roster',
      'school 3': 'http://page3/SportSelect.aspx',
    }
    actual = convert_roster_webpages_to_csv.parse_webpages(fake_webpages,
                                                           fake_urls)
    expected = {
      'school 1': team_a,
      'school 2': team_b,
      'school 3': team_c,
    }
    self.assertEqual(expected, actual)
    # The expected calls are actually 6, not 3, even though there are only 3
    # fake schools, because the "if page:" statement makes a __bool__ call on
    # the mock object.
    self.assertEqual(6, len(mock_bs.mock_calls))

  def test_set_csv_rows(self):
    fake_schools = ['School 1', 'School 2', 'School 3']
    fake_locations = ['Location 1', 'Location 2', 'Location 3']
    fake_states = ['State 1', 'State 2', 'State 3']
    fake_types = ['Type 1', 'Type 2', 'Type 3']
    fake_nicknames = ['Nickname 1', 'Nickname 2', 'Nickname 3']
    fake_conferences = ['Conference 1', 'Conference 2', 'Conference 3']
    fake_urls = {'School 1': 'http://roster.aspx',
                 'School 3': 'http://sports.roster'}
    fake_teams = {
      'School 1': [{'attr 1': 'Attribute 1'},
                   {'attr 2': 'Attribute 2'}],
      'School 2': [{'attr 3': 'Attribute 3'},
                   {'attr 4': 'Attribute 4'}],
      'School 3': [{'attr 5': 'Attribute 5'},
                   {'attr 6': 'Attribute 6'}],
    }
    actual = convert_roster_webpages_to_csv.set_csv_rows(fake_schools,
                                                         fake_locations,
                                                         fake_states,
                                                         fake_types,
                                                         fake_nicknames,
                                                         fake_conferences,
                                                         fake_urls,
                                                         fake_teams)
    expected = [
      'School 1,Location 1,State 1,Type 1,Nickname 1,Conference 1,http://roster.aspx,Attribute 1',
      'School 1,Location 1,State 1,Type 1,Nickname 1,Conference 1,http://roster.aspx,Attribute 2',
      'School 2,Location 2,State 2,Type 2,Nickname 2,Conference 2,,Attribute 3',
      'School 2,Location 2,State 2,Type 2,Nickname 2,Conference 2,,Attribute 4',
      'School 3,Location 3,State 3,Type 3,Nickname 3,Conference 3,http://sports.roster,Attribute 5',
      'School 3,Location 3,State 3,Type 3,Nickname 3,Conference 3,http://sports.roster,Attribute 6',
    ]
    self.assertEqual(expected, actual)


if __name__ == '__main__':
  unittest.main()
