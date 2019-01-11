"""Unit tests for download_roster_webpages.py"""
import unittest
from unittest import mock

import download_roster_webpages

class DownloadRosterWebPagesTest(unittest.TestCase):

  def test_format_request_args_expected_path_param(self):
    test_urls = [
      'https://acusports.com/roster.aspx?path=wsoc',
    ]
    actual_request_args, actual_corrected_urls = \
        download_roster_webpages.format_request_args(test_urls)
    expected_request_args = [{
      'url': 'https://acusports.com/roster.aspx',
      'params': {'path': 'wsoc'},
      'headers': download_roster_webpages.HTTP_HEADERS,
    }]
    expected_corrected_urls = [
      'https://acusports.com/roster.aspx?path=wsoc',
    ]
    # This setting prints out the full difference if assertEqual() fails.
    self.maxDiff = None
    self.assertEqual(expected_request_args, actual_request_args)
    self.assertEqual(expected_corrected_urls, actual_corrected_urls)

  def test_format_request_args_path_soccer(self):
    test_urls = [
      'https://floridagators.com/roster.aspx?roster=450&path=soccer',
    ]
    actual_request_args, actual_corrected_urls = \
        download_roster_webpages.format_request_args(test_urls)
    expected_request_args = [{
      'url': 'https://floridagators.com/roster.aspx',
      'params': {'roster': '450', 'path': 'soccer'},
      'headers': download_roster_webpages.HTTP_HEADERS,
    }]
    expected_corrected_urls = [
      'https://floridagators.com/roster.aspx?roster=450&path=soccer',
    ]
    # This setting prints out the full difference if assertEqual() fails.
    self.maxDiff = None
    self.assertEqual(expected_request_args, actual_request_args)
    self.assertEqual(expected_corrected_urls, actual_corrected_urls)

  def test_format_request_args_path_wsoccer(self):
    test_urls = [
      'https://fightinghawks.com/roster.aspx?path=wsoccer&roster=376',
    ]
    actual_request_args, actual_corrected_urls = \
        download_roster_webpages.format_request_args(test_urls)
    expected_request_args = [{
      'url': 'https://fightinghawks.com/roster.aspx',
      'params': {'path': 'wsoccer', 'roster': '376'},
      'headers': download_roster_webpages.HTTP_HEADERS,
    }]
    expected_corrected_urls = [
      'https://fightinghawks.com/roster.aspx?path=wsoccer&roster=376',
    ]
    # This setting prints out the full difference if assertEqual() fails.
    self.maxDiff = None
    self.assertEqual(expected_request_args, actual_request_args)
    self.assertEqual(expected_corrected_urls, actual_corrected_urls)

  def test_format_request_args_path_param_without_value(self):
    test_urls = [
      'https://gosoutheast.com/roster.aspx?roster=237&path=',
    ]
    actual_request_args, actual_corrected_urls = \
        download_roster_webpages.format_request_args(test_urls)
    expected_request_args = [{
      'url': 'https://gosoutheast.com/roster.aspx',
      'params': {'roster': '237', 'path': ''},
      'headers': download_roster_webpages.HTTP_HEADERS,
    }]
    expected_corrected_urls = [
      'https://gosoutheast.com/roster.aspx?roster=237&path=',
    ]
    # This setting prints out the full difference if assertEqual() fails.
    self.maxDiff = None
    self.assertEqual(expected_request_args, actual_request_args)
    self.assertEqual(expected_corrected_urls, actual_corrected_urls)

  def test_format_request_args_other_param_without_value(self):
    test_urls = [
      'https://mcneesesports.com/roster.aspx?path=wsoc&roster=',
    ]
    actual_request_args, actual_corrected_urls = \
        download_roster_webpages.format_request_args(test_urls)
    expected_request_args = [{
      'url': 'https://mcneesesports.com/roster.aspx',
      'params': {'path': 'wsoc', 'roster': ''},
      'headers': download_roster_webpages.HTTP_HEADERS,
    }]
    expected_corrected_urls = [
      'https://mcneesesports.com/roster.aspx?path=wsoc&roster=',
    ]
    # This setting prints out the full difference if assertEqual() fails.
    self.maxDiff = None
    self.assertEqual(expected_request_args, actual_request_args)
    self.assertEqual(expected_corrected_urls, actual_corrected_urls)

  def test_format_request_args_path_with_wrong_sport(self):
    test_urls = [
      'https://utahutes.com/roster.aspx?path=wbball',
    ]
    actual_request_args, actual_corrected_urls = \
        download_roster_webpages.format_request_args(test_urls)
    expected_request_args = [{
      'url': 'https://utahutes.com/roster.aspx',
      'params': {'path': 'wsoc'},
      'headers': download_roster_webpages.HTTP_HEADERS,
    }]
    expected_corrected_urls = [
      'https://utahutes.com/roster.aspx?path=wsoc',
    ]
    # This setting prints out the full difference if assertEqual() fails.
    self.maxDiff = None
    self.assertEqual(expected_request_args, actual_request_args)
    self.assertEqual(expected_corrected_urls, actual_corrected_urls)

  def test_format_request_args_sportselect_url(self):
    test_urls = [
      'http://www.lsusports.net/SportSelect.dbml?DB_OEM_ID=5200&SPID=2168&SPSID=27839',
    ]
    actual_request_args, actual_corrected_urls = \
        download_roster_webpages.format_request_args(test_urls)
    expected_request_args = [{
      'url': 'http://www.lsusports.net/SportSelect.dbml',
      'params': {'DB_OEM_ID': '5200', 'SPID': '2168', 'SPSID': '27839'},
      'headers': download_roster_webpages.HTTP_HEADERS,
    }]
    expected_corrected_urls = [
      'http://www.lsusports.net/SportSelect.dbml?DB_OEM_ID=5200&SPID=2168&SPSID=27839',
    ]
    # This setting prints out the full difference if assertEqual() fails.
    self.maxDiff = None
    self.assertEqual(expected_request_args, actual_request_args)
    self.assertEqual(expected_corrected_urls, actual_corrected_urls)

  @mock.patch('download_roster_webpages.requests')
  @mock.patch('download_roster_webpages.bs')
  def test_get_webpage_content(self, mock_bs, mock_requests):
    mock_bs.return_value = 'fake_content'
    mock_response = mock.MagicMock()
    mock_response.status_code = 200
    mock_response.headers = {'Content-Encoding': 'gzip'}
    mock_response.content = '<html>Roster</html>'
    mock_requests.get.return_value = mock_response
    fake_request_arg = {
      'url': 'http://www.lsusports.net/SportSelect.dbml',
      'params': {'DB_OEM_ID': '5200', 'SPID': '2168', 'SPSID': '27839'},
      'headers': download_roster_webpages.HTTP_HEADERS,
    }
    fake_request_args = [fake_request_arg]
    actual_soups = download_roster_webpages.get_webpage_content(fake_request_args)
    expected_soups = ['fake_content']
    # This setting prints out the full difference if assertEqual() fails.
    self.maxDiff = None
    self.assertEqual(expected_soups, actual_soups)
    mock_requests.get.assert_called_once_with(**fake_request_arg)
    mock_bs.assert_called_once_with('<html>Roster</html>', 'html.parser')

  @mock.patch('download_roster_webpages.roster_file_util')
  def test_save_files(self, mock_fu):
    mock_soup = mock.MagicMock()
    fake_html = '<html>Roster</html>'
    mock_soup.prettify.return_value = fake_html
    fake_soups = [mock_soup]
    fake_school_name = 'School 1'
    fake_schools = [fake_school_name]
    fake_roster_url = 'http://school1/roster.aspx'
    fake_urls = [fake_roster_url]
    fake_dir = '/foo/bar/biz'
    download_roster_webpages.save_files(fake_soups, fake_schools, fake_urls,
                                        fake_dir)
    expected_calls = [
      mock.call('School_1.webpage', fake_html, dir_path=fake_dir),
      mock.call('School_1.url', fake_roster_url, dir_path=fake_dir),
    ]
    # This setting prints out the full difference if assertEqual() fails.
    self.maxDiff = None
    self.assertEqual(expected_calls, mock_fu.write_file.mock_calls)


if __name__ == '__main__':
  unittest.main()
