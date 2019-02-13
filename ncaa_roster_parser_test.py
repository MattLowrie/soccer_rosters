"""Unit tests for ncaa_roster_parser.py"""
from bs4 import BeautifulSoup as bs
import unittest
from unittest import mock

import ncaa_roster_parser

class NcaaRosterParserTest(unittest.TestCase):

  ##############################################################################
  # ProcessorBase tests.
  ##############################################################################
  def test_processorbase_remove_extra_spaces(self):
    pb = ncaa_roster_parser.ProcessorBase('', '')
    test = "\t\t    St.  Joseph's   High    School      \n\t"
    actual = pb.remove_extra_spaces(test)
    self.assertEqual("St. Joseph's High School", actual)

  ##############################################################################
  # SidearmSportsDgrdProcessor tests.
  ##############################################################################
  def test_ssdgrdprocessor_format_hometown_and_state(self):
    ssdp = ncaa_roster_parser.SidearmSportsDgrdProcessor('')
    test = '  Tallahassee, Fla.  \n'
    actual_hometown, actual_state = ssdp.format_hometown_and_state(test)
    self.assertEqual('Tallahassee', actual_hometown)
    self.assertEqual('Fla.', actual_state)

  def test_ssdgrdprocessor_format_hometown_and_state_foreign_city(self):
    ssdp = ncaa_roster_parser.SidearmSportsDgrdProcessor('')
    test = '   Vancouver, British   Columbia,   Canada    \n'
    actual_hometown, actual_state = ssdp.format_hometown_and_state(test)
    self.assertEqual('Vancouver', actual_hometown)
    self.assertEqual('British Columbia, Canada', actual_state)

  def test_ssdgrdprocessor_format_slash_separated_data(self):
    ssdp = ncaa_roster_parser.SidearmSportsDgrdProcessor('')
    test = ' Anchorage, Alaska/Darlington School (Ga.)/Cook Inlet SC '
    actual_hometown, actual_state, actual_high_school, actual_club = \
        ssdp.format_slash_separated_data(test)
    self.assertEqual('Anchorage', actual_hometown)
    self.assertEqual('Alaska', actual_state)
    self.assertEqual('Darlington School (Ga.)', actual_high_school)
    self.assertEqual('Cook Inlet SC', actual_club)

  def test_ssdgrdprocessor_integration_test(self):
    test_content = None
    with open('testdata/UTSA.webpage', 'r') as fo:
      test_webpage = fo.read()
    test_content = bs(test_webpage, 'html.parser')
    ssdp = ncaa_roster_parser.SidearmSportsDgrdProcessor(test_content)
    actual_team = ssdp.get_team()
    self.assertEqual(31, len(actual_team))
    expected_columns = ['name', 'jersey', 'position', 'height', 'hometown',
        'home_state', 'high_school', 'year', 'club']
    self.assertEqual(expected_columns, list(actual_team[0].keys()))
    # Verify that hometown/state/high school/club get parsed correctly
    expected_player = {
      'name': 'Michelle Cole',
      'jersey': '0',
      'position': 'GK',
      'height': '5-11',
      'hometown': 'Anchorage',
      'home_state': 'Alaska',
      'high_school': 'Darlington School (Ga.)',
      'year': 'Sr.',
      'club': 'Cook Inlet SC',
    }
    self.assertDictEqual(expected_player, actual_team[0])

  ##############################################################################
  # SidearmSportsSidearmClassNameProcessor tests.
  ##############################################################################
  def test_sidearmsportssidearmclassnameprocessor_get_player_name(self):
    test_html = """
        <div class="sidearm-roster-player-name">
            <span class="sidearm-roster-player-jersey flex flex-inline">
            <span class="sidearm-roster-player-jersey-number">
                11
            </span>
            </span>
            <p>
            <a aria-label="Julie Foudy - View Full Bio" data-bind="click: function() { return true; }, clickBubble: false" href="/roster.aspx?rp_id=3223">
                Julie Foudy
            </a>
            </p>
        </div>
    """
    test_player = bs(test_html, 'html.parser')
    ssscnp = ncaa_roster_parser.SidearmSportsSidearmClassNameProcessor('')
    actual = ssscnp.get_player_name(test_player)
    self.assertEqual('Julie Foudy', actual)

  def test_sidearmsportssidearmclassnameprocessor_get_player_jersey(self):
    test_html = """
        <div class="sidearm-roster-player-name">
            <span class="sidearm-roster-player-jersey flex flex-inline">
            <span class="sidearm-roster-player-jersey-number">
                11
            </span>
            </span>
            <p>
            <a aria-label="Julie Foudy - View Full Bio" data-bind="click: function() { return true; }, clickBubble: false" href="/roster.aspx?rp_id=3223">
                Julie Foudy
            </a>
            </p>
        </div>
    """
    test_player = bs(test_html, 'html.parser')
    ssscnp = ncaa_roster_parser.SidearmSportsSidearmClassNameProcessor('')
    actual = ssscnp.get_player_jersey(test_player)
    self.assertEqual('11', actual)

  def test_sidearmsportssidearmclassnameprocessor_get_player_position(self):
    test_html = """
        <div class="sidearm-roster-player-position">
            <span class="text-bold">
            <span class="sidearm-roster-player-position-long-short hide-on-small-down">
                Forward
            </span>
            <span class="sidearm-roster-player-position-long-short hide-on-medium">
                F
            </span>
        </div>
    """
    test_player = bs(test_html, 'html.parser')
    ssscnp = ncaa_roster_parser.SidearmSportsSidearmClassNameProcessor('')
    actual = ssscnp.get_player_position(test_player)
    self.assertEqual('F', actual)

  def test_sidearmsportssidearmclassnameprocessor_get_player_height(self):
    test_html = """
        <div class="sidearm-roster-player-position">
            <span class="text-bold">
            <span class="sidearm-roster-player-position-long-short hide-on-small-down">
                Forward
            </span>
            <span class="sidearm-roster-player-position-long-short hide-on-medium">
                F
            </span>
            <span class="sidearm-roster-player-height">
                5'7"
            </span>
        </div>
    """
    test_player = bs(test_html, 'html.parser')
    ssscnp = ncaa_roster_parser.SidearmSportsSidearmClassNameProcessor('')
    actual = ssscnp.get_player_height(test_player)
    self.assertEqual('5\'7"', actual)

  def test_sidearmsportssidearmclassnameprocessor_get_player_hometown_and_home_state(self):
    test_html = """
        <div class="sidearm-roster-player-other hide-on-large">
            <div class="sidearm-roster-player-class-hometown">
            <span class="sidearm-roster-player-academic-year hide-on-large">
                So.
            </span>
            <span class="sidearm-roster-player-hometown">
                Lexington, S.C.
            </span>
            <span class="sidearm-roster-player-highschool">
                River Bluff
            </span>
            </div>
            <div class="sidearm-roster-player-bio hide-on-small-down">
            <a aria-label="View Full Bio" data-bind="click: function() { return true; }, clickBubble: false" href="/roster.aspx?rp_id=5647">
                Full Bio
            </a>
            </div>
        </div>
    """
    test_player = bs(test_html, 'html.parser')
    ssscnp = ncaa_roster_parser.SidearmSportsSidearmClassNameProcessor('')
    actual_hometown, actual_home_state = \
        ssscnp.get_player_hometown_and_home_state(test_player)
    self.assertEqual('Lexington', actual_hometown)
    self.assertEqual('S.C.', actual_home_state)

  def test_sidearmsportssidearmclassnameprocessor_get_player_high_school(self):
    test_html = """
        <div class="sidearm-roster-player-other hide-on-large">
            <div class="sidearm-roster-player-class-hometown">
            <span class="sidearm-roster-player-academic-year hide-on-large">
                So.
            </span>
            <span class="sidearm-roster-player-hometown">
                Lexington, S.C.
            </span>
            <span class="sidearm-roster-player-highschool">
                River Bluff
            </span>
            </div>
            <div class="sidearm-roster-player-bio hide-on-small-down">
            <a aria-label="View Full Bio" data-bind="click: function() { return true; }, clickBubble: false" href="/roster.aspx?rp_id=5647">
                Full Bio
            </a>
            </div>
        </div>
    """
    test_player = bs(test_html, 'html.parser')
    ssscnp = ncaa_roster_parser.SidearmSportsSidearmClassNameProcessor('')
    actual_high_school = ssscnp.get_player_high_school(test_player)
    self.assertEqual('River Bluff', actual_high_school)

  def test_sidearmsportssidearmclassnameprocessor_get_player_high_school_from_previous_school(self):
    test_html = """
        <div class="sidearm-roster-player-other hide-on-large">
            <div class="sidearm-roster-player-class-hometown">
            <span class="sidearm-roster-player-academic-year hide-on-large">
                Sr.
            </span>
            <span class="sidearm-roster-player-hometown">
                Highlands Ranch, Colo.
            </span>
            <span class="sidearm-roster-player-previous-school">
                Thunder Ridge HS
            </span>
            </div>
            <div class="sidearm-roster-player-bio hide-on-small-down">
            <a aria-label="View Full Bio" data-bind="click: function() { return true; }, clickBubble: false" href="/roster.aspx?rp_id=4180">
            Full Bio
            </a>
            </div>
        </div>
    """
    test_player = bs(test_html, 'html.parser')
    ssscnp = ncaa_roster_parser.SidearmSportsSidearmClassNameProcessor('')
    ssscnp.logger = mock.MagicMock()
    actual_high_school = ssscnp.get_player_high_school(test_player)
    self.assertTrue(ssscnp.logger.warning.called)
    self.assertEqual(2, ssscnp.logger.warning.call_count)
    self.assertEqual('Thunder Ridge HS', actual_high_school)

  def test_sidearmsportssidearmclassnameprocessor_get_player_year(self):
    test_html = """
        <div class="sidearm-roster-player-other flex-item-1 columns hide-on-medium-down">
          <div class="sidearm-roster-player-class-hometown">
            <span class="sidearm-roster-player-academic-year">
                Sophomore
            </span>
            <span class="sidearm-roster-player-hometown">
                Dublin, Ireland
            </span>
            <span class="sidearm-roster-player-previous-school">
                Oakland University
            </span>
          </div>
          <div class="sidearm-roster-player-bio">
            <a aria-label="View Full Bio" data-bind="click: function() { return true; }, clickBubble: false" href="/roster.aspx?rp_id=4503">
                Full Bio
            </a>
          </div>
        </div>
    """
    test_player = bs(test_html, 'html.parser')
    ssscnp = ncaa_roster_parser.SidearmSportsSidearmClassNameProcessor('')
    actual_high_school = ssscnp.get_player_year(test_player)
    self.assertEqual('Sophomore', actual_high_school)

  def test_sidearmsportssidearmclassnameprocessor_get_player_club(self):
    test_html = """
        <div class="sidearm-roster-player-position">
            <span class="text-bold">
                M
            </span>
            <span class="sidearm-roster-player-height">
                5'2"
            </span>
            <span class="sidearm-roster-player-custom1">
                FC Star of Mass ECNL
            </span>
        </div>
    """
    test_player = bs(test_html, 'html.parser')
    ssscnp = ncaa_roster_parser.SidearmSportsSidearmClassNameProcessor('')
    actual_high_school = ssscnp.get_player_club(test_player)
    self.assertEqual('FC Star of Mass ECNL', actual_high_school)

  def test_sidearmsportssidearmclassnameprocessor_integration_test(self):
    test_content = None
    with open('testdata/Southeastern_Louisiana.webpage', 'r') as fo:
      test_webpage = fo.read()
    test_content = bs(test_webpage, 'html.parser')
    ssscnp = \
        ncaa_roster_parser.SidearmSportsSidearmClassNameProcessor(test_content)
    actual_team = ssscnp.get_team()
    self.assertEqual(26, len(actual_team))
    expected_columns = ['name', 'jersey', 'position', 'height', 'hometown',
        'home_state', 'high_school', 'year', 'club']
    self.assertEqual(expected_columns, list(actual_team[0].keys()))

  ##############################################################################
  # SportSelectProcessor tests.
  ##############################################################################
  def test_sportselectprocessor_get_player_name(self):
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

  def test_sportselectprocessor_get_player_jersey(self):
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

  def test_sportselectprocessor_get_player_height(self):
    test_html = """
        <div class="height">
            5'7"
        </div>
    """
    test_content = bs(test_html, 'html.parser')
    ssp = ncaa_roster_parser.SportSelectProcessor('')
    actual = ssp.get_player_height(test_content)
    self.assertEqual('5\'7"', actual)

  def test_sportselectprocessor_get_player_position(self):
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

  def test_sportselectprocessor_get_player_year(self):
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

  def test_sportselectprocessor_get_hometown_homestate_highschool_club(self):
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

  def test_sportselectprocessor_get_hometown_split_on_first_comma(self):
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

  def test_sportselectprocessor_get_hometown_homestate(self):
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

  def test_sportselectprocessor_integration_test(self):
    test_content = None
    with open('testdata/Nebraska.webpage', 'r') as fo:
      test_webpage = fo.read()
    test_content = bs(test_webpage, 'html.parser')
    ssp = ncaa_roster_parser.SportSelectProcessor(test_content)
    actual_team = ssp.get_team()
    self.assertEqual(26, len(actual_team))
    expected_columns = ['name', 'jersey', 'position', 'height', 'hometown',
        'home_state', 'high_school', 'year', 'club']
    self.assertEqual(expected_columns, list(actual_team[0].keys()))

  ##############################################################################
  # HtmlTableProcessor tests.
  ##############################################################################
  def test_htmltableprocessor_get_player_name(self):
    test_html = """
    <tr>
        <td class="number">
            <span class="label">
             No.:
            </span>
            0
        </td>
        <th class="name" scope="row">
            <a aria-label="Julie Ertz: jersey number 0: full bio" href="/sports/wsoc/2018-19/bios/ertz">
                <img alt="Julie Ertz full bio" class="headshot lazyload" data-src="/sports/wsoc/2018-19/photos/0001/Ertz-049.jpg?max_width=300" src="/info/images/spacer.gif"/>
             Julie Ertz
            </a>
        </th>
    </tr>
    """
    test_player = bs(test_html, 'html.parser')
    htp = ncaa_roster_parser.HtmlTableProcessor('')
    actual = htp.get_player_name(test_player)
    self.assertEqual('Julie Ertz', actual)

  def test_htmltableprocessor_get_labels_and_data(self):
    test_html = """
        <tr>
            <td class="number">
                <span class="label">
                    No.:
                </span>
                    0
            </td>
            <th class="name" scope="row">
                <a aria-label="Abby Wambach: jersey number 0: full bio" href="/sports/wsoc/2018-19/bios/wambach_abby_c6s8">
                <img alt="Abby Wambach full bio" class="headshot lazyload" data-src="/sports/wsoc/2018-19/photos/wambach-20180808wsoc-0107.jpg?max_width=300" src="/info/images/spacer.gif"/>
                    Abby
		        		    			    				 
    			    			    	    		    									Wambach
                </a>
            </th>
            <td>
                <span class="label">
                    Cl.:
                </span>
                    Freshman
            </td>
            <td>
            <span class="label">
                 Pos.:
            </span>
                GK
            </td>
            <td>
                <span class="label">
                    Ht.:
                </span>
                    5-9
            </td>
            <td>
                <span class="label">
                    Hometown/High School:
                </span>
                    Grand Island, NY
		        		    			    				/
    			    			    	    		    									St. Dominion HS
            </td>
            <td>
                <span class="label">
                    Major:
                </span>
                    Exercise Science
            </td>
        </tr>
    """
    test_player = bs(test_html, 'html.parser')
    htp = ncaa_roster_parser.HtmlTableProcessor('')
    actual = htp.get_labels_and_data(test_player)
    expected = {
      'no.:': '0',
      'cl.:': 'Freshman',
      'pos.:': 'GK',
      'ht.:': '5-9',
      'hometown': 'Grand Island',
      'state': 'NY',
      'high school:': 'St. Dominion HS',
      'major:': 'Exercise Science',
    }
    self.assertDictEqual(expected, actual)

  def test_htmltableprocessor_integration_test(self):
    test_content = None
    with open('testdata/Cal_Poly.webpage', 'r') as fo:
      test_webpage = fo.read()
    test_content = bs(test_webpage, 'html.parser')
    htp = ncaa_roster_parser.HtmlTableProcessor(test_content)
    actual_team = htp.get_team()
    self.assertEqual(34, len(actual_team))
    expected_columns = ['name', 'jersey', 'position', 'height', 'hometown',
        'home_state', 'high_school', 'year', 'club']
    self.assertEqual(expected_columns, list(actual_team[0].keys()))


if __name__ == '__main__':
  unittest.main()
