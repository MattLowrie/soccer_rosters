# -*- coding: utf-8 -*-

import unittest
from unittest import mock
import lib_wiki


COL_HEADS = ['Institution', 'Location', 'State', 'Type', 'Nickname', 'Conference']
ACU = ['Abilene Christian', 'Abilene', 'Texas', 'Private', 'Wildcats', 'Southland']
CU = ['Colorado', 'Boulder', 'Colorado', 'Public', 'Buffalos', 'Pac-12']
SHS = ['Sam Houston State', 'Huntsville', 'Texas', 'Public', 'Peahens', 'Metro Atlantic']
STANFORD = ['Stanford', 'Palo Alto', 'California', 'Private', 'Cardinal', 'Pac-12']
YSU = ['Youngstown State', 'Youngstown', 'Ohio', 'Public', 'Penguins', 'Horizon']
FAKE_ROWS = []
FAKE_ROWS.append(dict(zip(COL_HEADS, ACU)))
FAKE_ROWS.append(dict(zip(COL_HEADS, CU)))
FAKE_ROWS.append(dict(zip(COL_HEADS, SHS)))
FAKE_ROWS.append(dict(zip(COL_HEADS, STANFORD)))
FAKE_ROWS.append(dict(zip(COL_HEADS, YSU)))
FAKE_TABLE = mock.MagicMock()
FAKE_TABLE.rows = FAKE_ROWS
FAKE_WIKITABLE = [
  FAKE_TABLE,
]

class TestLibWiki(unittest.TestCase):

  @mock.patch('lib_wiki.import_tables')
  def testGetWomensSoccerArticleTable(self, mock_import_tables):
    mock_import_tables.return_value = FAKE_WIKITABLE
    actual = lib_wiki.GetWomensSoccerArticleTable()
    self.assertTrue(True)

if __name__ == '__main__':
  unittest.main()
