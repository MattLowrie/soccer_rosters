"""Unit tests for ncaa_roster_parser.py"""
from bs4 import BeautifulSoup as bs
import unittest
from unittest import mock

import ncaa_roster_parser

class NcaaRosterParserTest(unittest.TestCase):

  def test_ss_dgrd_processor_clean_text(self):
    proc = ncaa_roster_parser.SidearmSportsDgrdProcessor('')
    test = "    St.  Joseph's   High    School      \n\t"
    actual = proc.clean_text(test)
    self.assertEqual("St. Joseph's High School", actual)

  def test_ss_dgrd_processor_format_hometown_and_state(self):
    proc = ncaa_roster_parser.SidearmSportsDgrdProcessor('')
    test = '  Tallahassee, Fla.  \n'
    actual_hometown, actual_state = proc.format_hometown_and_state(test)
    self.assertEqual('Tallahassee', actual_hometown)
    self.assertEqual('Fla.', actual_state)

  def test_ss_dgrd_processor_format_slash_separated_data(self):
    proc = ncaa_roster_parser.SidearmSportsDgrdProcessor('')
    test = ' Anchorage, Alaska/Darlington School (Ga.)/Cook Inlet SC '
    actual_hometown, actual_state, actual_high_school, actual_club = \
        proc.format_slash_separated_data(test)
    self.assertEqual('Anchorage', actual_hometown)
    self.assertEqual('Alaska', actual_state)
    self.assertEqual('Darlington School (Ga.)', actual_high_school)
    self.assertEqual('Cook Inlet SC', actual_club)

  def test_sport_select_processor_get_player_name(self):
    test_html = """
        <div class="player-name">
            <a href="/ViewArticle.dbml?ATCLID=211651929&amp;DB_OEM_ID=27200&amp;Q_SEASON=2018" title="Kat Zaber">
                Kat Zaber
            </a>
        </div>
    """
    test_content = bs(test_html, 'html.parser')
    ssp = ncaa_roster_parser.SportSelectProcessor('')
    actual = ssp.get_player_name(test_content)
    self.assertEqual('Kat Zaber', actual)

  def test_sport_select_processor_get_player_jersey(self):
    test_html = """
        <div class="image relative left">
            <a href="/ViewArticle.dbml?ATCLID=210212875&amp;DB_OEM_ID=33100&amp;Q_SEASON=2018" title="Caroline Wallace">
                <img alt="Caroline Wallace" border="0" src="https://neulioncs.hs.llnwd.net/pics33/200/VL/VLMUUNVFCXIZYCD.20180821183616.jpg"/>
                <div class="number">
                    #33
                </div>
            </a>
        </div>
    """
    test_content = bs(test_html, 'html.parser')
    ssp = ncaa_roster_parser.SportSelectProcessor('')
    actual = ssp.get_player_jersey(test_content)
    self.assertEqual('33', actual)

  def test_sport_select_processor_get_player_height(self):
    test_html = """
        <div class="height">
            5'7"
        </div>
    """
    test_content = bs(test_html, 'html.parser')
    ssp = ncaa_roster_parser.SportSelectProcessor('')
    actual = ssp.get_player_height(test_content)
    self.assertEqual('5\'7"', actual)

  def test_sport_select_processor_get_player_position(self):
    test_html = """
        <div class="info">
            <div class="position">
                <span class="field">
                    Position:
                </span>
                <span class="data">
                    Defender
                </span>
            </div>
            <div class="year">
                <span class="field">
                    Year:
                </span>
                <span class="data">
                    Fr.
                </span>
           </div>
        </div>
    """
    test_content = bs(test_html, 'html.parser')
    ssp = ncaa_roster_parser.SportSelectProcessor('')
    actual = ssp.get_player_position(test_content)
    self.assertEqual('Defender', actual)

  def test_sport_select_processor_get_player_year(self):
    test_html = """
        <div class="info">
            <div class="position">
                <span class="field">
                    Position:
                </span>
                <span class="data">
                    Defender
                </span>
            </div>
            <div class="year">
                <span class="field">
                    Year:
                </span>
                <span class="data">
                    Fr.
                </span>
           </div>
        </div>
    """
    test_content = bs(test_html, 'html.parser')
    ssp = ncaa_roster_parser.SportSelectProcessor('')
    actual = ssp.get_player_year(test_content)
    self.assertEqual('Fr.', actual)

  def test_sport_select_processor_get_hometown_homestate_highschool_club(self):
    test_html = """
        <div class="hometown">
            <span class="field">
                Hometown:
            </span>
            <span class="data" title="Marietta, Ga.  (St. Joseph's HS ) (Match Fit Academy NE-NPL )">
                Marietta, Ga.  (St. Joseph's HS ) (Match Fit Academy NE-NPL )
            </span>
        </div>
    """
    test_player = bs(test_html, 'html.parser')
    ssp = ncaa_roster_parser.SportSelectProcessor('')
    actual_hometown, actual_home_state, actual_high_school, actual_club = \
        ssp.get_hometown_homestate_highschool_club(test_player)
    self.assertEqual('Marietta', actual_hometown)
    self.assertEqual('Ga.', actual_home_state)
    self.assertEqual('St. Joseph\'s HS', actual_high_school)
    self.assertEqual('Match Fit Academy NE-NPL', actual_club)

  def test_sport_select_processor_get_hometown_split_on_first_comma(self):
    test_html = """
        <div class="hometown">
            <span class="field">
                Hometown:
            </span>
            <span class="data" title="Epsom, St.Mary, Jamaica (Titchfield HS/Southeastern)">
                Epsom, St.Mary, Jamaica (Titchfield HS/Southeastern)
            </span>
        </div>
    """
    test_player = bs(test_html, 'html.parser')
    ssp = ncaa_roster_parser.SportSelectProcessor('')
    actual_hometown, actual_home_state, actual_high_school, actual_club = \
        ssp.get_hometown_homestate_highschool_club(test_player)
    self.assertEqual('Epsom', actual_hometown)
    self.assertEqual('St.Mary Jamaica', actual_home_state)
    self.assertEqual('Titchfield HS/Southeastern', actual_high_school)
    self.assertEqual('', actual_club)

  def test_sport_select_processor_get_hometown_homestate(self):
    test_html = """
        <div class="hometown">
            <span class="field">
                Hometown:
            </span>
            <span class="data" title="Helotes, Texas">
                Helotes, Texas
            </span>
        </div>
    """
    test_player = bs(test_html, 'html.parser')
    ssp = ncaa_roster_parser.SportSelectProcessor('')
    actual_hometown, actual_home_state, actual_high_school, actual_club = \
        ssp.get_hometown_homestate_highschool_club(test_player)
    self.assertEqual('Helotes', actual_hometown)
    self.assertEqual('Texas', actual_home_state)
    self.assertEqual('', actual_high_school)
    self.assertEqual('', actual_club)

  def test_sport_select_processor_integration_test(self):
    test_content = None
    with open('testdata/nebraska.webpage', 'r') as fo:
      test_webpage = fo.read()
    test_content = bs(test_webpage, 'html.parser')
    ssp = ncaa_roster_parser.SportSelectProcessor(test_content)
    actual_team = ssp.get_team()
    self.assertEqual(26, len(actual_team))
    expected_columns = ['name', 'jersey', 'position', 'height', 'hometown',
        'home_state', 'high_school', 'year', 'club']
    self.assertEqual(expected_columns, list(actual_team[0].keys()))


if __name__ == '__main__':
  unittest.main()
