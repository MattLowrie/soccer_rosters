from unittest import mock
import unittest

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
    expected_webpages = [
      {'school 1': '<html page 1>'},
      {'school 2': '<html page 2>'},
    ]
    expected_urls = [
      {'school 1': fake_content[0]},
      {'school 2': fake_content[2]},
    ]
    self.assertEqual(expected_webpages, actual_webpages)
    self.assertEqual(expected_urls, actual_urls)

  @mock.patch('convert_roster_webpages_to_csv.ncaa_roster_parser')
  def test_parse_webpages(self, mock_nrp):
    mock_sidearm = mock.MagicMock()
    mock_table = mock.MagicMock()
    mock_sport_select = mock.MagicMock()
    mock_nrp.SidearmProcessor.return_value = mock_sidearm
    mock_nrp.HtmlTableProcessor.return_value = mock_table
    mock_nrp.SportSelectProcessor.return_value = mock_sport_select
    mock_sidearm.get_team.return_value = 'team1'
    mock_table.get_team.return_value = 'team2'
    mock_sport_select.get_team.return_value = 'team3'
    fake_webpages = [
      {'school 1': '<html page 1>'},
      {'school 2': '<html page 2>'},
      {'school 3': '<html page 3>'},
    ]
    fake_urls = [
      {'school 1': 'http://page1/roster.aspx'},
      {'school 2': 'http://page2/2018-19/roster'},
      {'school 3': 'http://page3/SportSelect.aspx'},
    ]
    actual = convert_roster_webpages_to_csv.parse_webpages(fake_webpages,
                                                           fake_urls)
    expected = ['team1', 'team2', 'team3']
    self.assertEqual(expected, actual)


if __name__ == '__main__':
  unittest.main()
