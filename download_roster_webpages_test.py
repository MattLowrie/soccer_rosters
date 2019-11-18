"""Unit tests for download_roster_webpages.py"""
import unittest
from unittest import mock

import download_roster_webpages

class DownloadRosterWebPagesTest(unittest.TestCase):

  @mock.patch('download_roster_webpages.user_agent')
  def test_build_request_args(self, mock_ua):
    mock_ua.generate_user_agent.return_value = 'Mozilla'
    test_url = 'https://wossamotta.u/roster.aspx'
    actual = download_roster_webpages._build_request_args(test_url)
    expected = {
      'url': test_url,
      'headers' : {
        'User-Agent': 'Mozilla',
        'Accept': download_roster_webpages.HTTP_HEADERS['Accept'],
        'Accept-Encoding': download_roster_webpages.HTTP_HEADERS['Accept-Encoding'],
        'Accept-Language': download_roster_webpages.HTTP_HEADERS['Accept-Language']
      }
    }
    self.assertEqual(expected, actual)

  @mock.patch('download_roster_webpages._build_request_args')
  @mock.patch('download_roster_webpages.requests')
  @mock.patch('download_roster_webpages.bs')
  def test_get_webpage_content(self, mock_bs, mock_requests, mock_bra):
    mock_bs.return_value = 'fake_content'
    mock_response = mock.MagicMock()
    mock_response.status_code = 200
    mock_response.headers = {'Content-Encoding': 'gzip'}
    mock_response.content = '<html>Roster</html>'
    mock_requests.get.return_value = mock_response
    test_url = 'http://www.quahog.univ/SportSelect.dbml'
    fake_request_arg = {
      'url': test_url,
      'headers': {'User-Agent': 'Mozilla'}
    }
    mock_bra.return_value = fake_request_arg
    actual = download_roster_webpages.get_webpage_content([test_url])
    expected = ['fake_content']
    # This setting prints out the full difference if assertEqual() fails.
    self.maxDiff = None
    self.assertEqual(expected, actual)
    mock_requests.get.assert_called_once_with(**fake_request_arg)
    mock_bs.assert_called_once_with('<html>Roster</html>', 'html.parser')

  @mock.patch('download_roster_webpages.LOGGER')
  @mock.patch('download_roster_webpages._build_request_args')
  @mock.patch('download_roster_webpages.requests')
  def test_get_webpage_content_server_error(self, mock_requests, mock_bra,
                                            mock_logger):
    mock_response = mock.MagicMock()
    mock_response.status_code = 500
    mock_response.headers = {'Content-Encoding': 'gzip'}
    mock_response.content = '<html>Roster</html>'
    mock_requests.get.return_value = mock_response
    test_url = 'http://www.greendalecc.edu/roster.aspx'
    fake_request_arg = {
      'url': test_url,
      'headers': {'User-Agent': 'Mozilla'}
    }
    mock_bra.return_value = fake_request_arg
    actual = download_roster_webpages.get_webpage_content([test_url])
    expected = [download_roster_webpages.DL_ERR_MSG]
    # This setting prints out the full difference if assertEqual() fails.
    self.maxDiff = None
    self.assertEqual(expected, actual)
    mock_requests.get.assert_called_once_with(**fake_request_arg)
    self.assertEqual(4, mock_logger.error.call_count)

  @mock.patch('download_roster_webpages.roster_file_util')
  def test_save_files(self, mock_fu):
    mock_soup = mock.MagicMock()
    fake_html = '<html>Roster</html>'
    mock_soup.prettify.return_value = fake_html
    fake_soups = [mock_soup]
    fake_school_name = 'School 1'
    fake_schools = [fake_school_name]
    fake_dir = '/foo/bar/biz'
    download_roster_webpages.save_files(fake_soups, fake_schools, fake_dir)
    expected_calls = [
      mock.call('School_1.webpage', fake_html, dir_path=fake_dir),
    ]
    # This setting prints out the full difference if assertEqual() fails.
    self.maxDiff = None
    self.assertEqual(expected_calls, mock_fu.write_file.mock_calls)


if __name__ == '__main__':
  unittest.main()
