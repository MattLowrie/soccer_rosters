"""Unit tests for roster_file_util.py"""
import csv
import os
import unittest
from unittest import mock
from unittest.mock import mock_open
import roster_file_util


TEST_CSV = """Institution,Location,State,Type,Nickname,Conference,Url
School 1,City 1,State 1,Public,Wasps,Conf 123,https://roster
Abilene Christian,Abilene,Texas,Private,Wildcats,Southland,https://acusports.com/roster.aspx?roster=286&path=wsoc
Air Force,Colorado Springs,Colorado,U.S. Service Academy,Falcons,Mountain West,https://goairforcefalcons.com/roster.aspx?roster=247&path=wsoc
Akron,Akron,Ohio,Public,Zips,MAC,https://gozips.com/roster.aspx?roster=206&path=wsoc
"""


class RosterFileUtilTest(unittest.TestCase):

  @mock.patch('roster_file_util.csv')
  def tesread_school_info_file(self, mock_csv):
    with mock.patch('roster_file_util.open',
                    mock.mock_open(read_data=TEST_CSV)) as mock_fo:
      mock_csv.DictReader.return_value = csv.DictReader(TEST_CSV)
      actual = roster_file_util.read_school_info_file('fake_file')
      print(actual)
      self.assertTrue(False)

  def test_write_file(self):
    mo = mock_open()
    with mock.patch('roster_file_util.open', mo):
      roster_file_util.write_file('fake_file', 'fake_content')
      expected_calls = [
        mock.call('fake_file', 'w', encoding='utf-8'),
        mock.call().__enter__(),
        mock.call().write('fake_content'),
        mock.call().__exit__(None, None, None),
      ]
      self.assertEqual(expected_calls, mo.mock_calls)

  @mock.patch('roster_file_util.os')
  def test_write_file_with_dir_path(self, mock_os):
    expected_file_path = os.path.join('fake_dir', 'fake_file')
    mock_os.path.join.return_value = expected_file_path
    mo = mock_open()
    with mock.patch('roster_file_util.open', mo):
      roster_file_util.write_file('fake_file', 'fake_content', 'fake_dir')
      expected_calls = [
        mock.call(expected_file_path, 'w', encoding='utf-8'),
        mock.call().__enter__(),
        mock.call().write('fake_content'),
        mock.call().__exit__(None, None, None),
      ]
      self.assertEqual(expected_calls, mo.mock_calls)
      mock_os.makedirs.assert_called_once_with('fake_dir',
                                              exist_ok=True)
      mock_os.path.join.assert_called_once_with('fake_dir', 'fake_file')

  @mock.patch('roster_file_util.os')
  def test_write_file_with_multiple_dir_path(self, mock_os):
    expected_path = os.path.join('fake_one', 'fake_two', 'fake_three')
    expected_file_path = os.path.join(expected_path, 'fake_file')
    mock_os.path.join.return_value = expected_file_path
    mo = mock_open()
    with mock.patch('roster_file_util.open', mo):
      roster_file_util.write_file('fake_file', 'fake_content',
                                  expected_path)
      expected_calls = [
        mock.call(expected_file_path, 'w', encoding='utf-8'),
        mock.call().__enter__(),
        mock.call().write('fake_content'),
        mock.call().__exit__(None, None, None),
      ]
      self.assertEqual(expected_calls, mo.mock_calls)
      mock_os.makedirs.assert_called_once_with(expected_path,
                                               exist_ok=True)
      mock_os.path.join.assert_called_once_with(expected_path, 'fake_file')


if __name__ == '__main__':
  unittest.main()
