"""Unit tests for ncaa_roster_parser.py"""
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


if __name__ == '__main__':
  unittest.main()
