"""Classes for parsing different roster page HTML schemas.

Classes:
  HtmlTableProcessor: For generic HTML tables.
"""
import logging
import re
from bs4 import BeautifulSoup as bs


class ProcessorBase(object):
  """Base class for implementing roster webpage processors.

  Attributes:
    name: A string of the current player's name when processing players.
    jersey: A string of the current player's jersey number.
    position: A string of the current player's position.
    height: A string of the current player's height.
    year: A string of the current player's year in school.
    hometown: A string of the current player's hometown.
    home_state: A string of the current player's home state.
    high_school: A string of the current player's high school, if provided.
    club: A string of the current player's club, if provided.
    team: A list of dicts containing each player's data.
  """

  name = ''
  jersey = ''
  position = ''
  height = ''
  hometown = ''
  home_state = ''
  high_school = ''
  year = ''
  club = ''
  team = []

  def __init__(self, content, logger_name):
    self.logger = logging.getLogger(logger_name)
    self.content = content

  def remove_extra_spaces(self, text):
    return ' '.join([s.strip() for s in text.split()])

  def add_player_to_team(self):
    if self.name:
      self.team.append({
        'name': self.name,
        'jersey': self.jersey,
        'position': self.position,
        'height': self.height,
        'hometown': self.hometown,
        'home_state': self.home_state,
        'high_school': self.high_school,
        'year': self.year,
        'club': self.club,
      })
    # Reset the class attributes for the next player.
    self.name = self.jersey = self.position = self.height = self.hometown = \
        self.home_state = self.high_school = self.year = self.club = ''

  def get_team(self):
    """Subclasses should override this function."""
    raise Exception("Not implemented.")


class HtmlTableProcessor(object):
  """Parses generic HTML tables where the category is the class attribute name."""

  def __init__(self, content):
    self.logger = logging.getLogger('HtmlTableProcessor')
    self.content = content

  def get_team(self):
    name = jersey = position = height = hometown = \
        home_state = high_school = year = club = ''
    team = []
    rows = self.content.findAll('tr')
    for row in rows:
      tds = row.select('td')
      if tds:
        ths = row.select('th')
        if ths:
          name = ' '.join(ths[0].get_text().split())
      for td in tds:
        spans = td.select('span')
        if spans:
          label_text = td.select('span')[0].get_text().strip()
          data_text = td.get_text()
          data_text = data_text.replace(label_text, '')
          slash_split = re.compile('/(?!F|M|D)')
          labels = slash_split.split(label_text)
          # self.logger.debug(labels)
          datas = slash_split.split(data_text)
          # self.logger.debug(datas)
          for i, data in enumerate(datas):
            label = ''
            try:
              label = labels[i].strip().lower()
            except IndexError:
              self.logger.error(
                'labels[%d] != datas[%d]', len(labels), len(datas))
              self.logger.debug(labels)
              self.logger.debug(datas)
            self.logger.debug('Label: %s', label)
            data = ' '.join(data.split())
            # All labels have been split, stripped of whitespace and converted
            # to lowercase at this point
            if 'no' in label:
              jersey = data
            elif 'pos' in label:
              position = data
            elif True in [x in label for x in ['yr', 'cl', 'year']]:
              year = data
            elif 'hometown' in label:
              hometown_text = data
              self.logger.debug(hometown_text)
              if ',' in hometown_text:
                hometown, home_state = hometown_text.split(',', 1)
                hometown = hometown.strip()
                home_state = home_state.replace(',', '').strip()
            elif True in [x in label for x in ['high', 'prev', 'last']]:
              high_school = data
            elif True in [x in label for x in ['ht', 'height']]:
              height = data
            elif 'club' in label:
              club = data
            else:
              self.logger.debug('Could not find specifier for label: %s', label)
      if name:
        team.append({
          'name': name,
          'jersey': jersey,
          'position': position,
          'height': height,
          'hometown': hometown,
          'home_state': home_state,
          'high_school': high_school,
          'year': year,
          'club': club,
        })
        name = jersey = position = height = hometown = \
            home_state = high_school = year = club = ''
    return team


class SidearmSportsDgrdProcessor(object):
  """For SidearmSports sites that use the "dgrd" prefix for class names.

  Some roster sites created by SidearmSports use the "dgrd" (I'm assuming this
  stands for "data grid"?) prefix and have a different DOM structure than other
  SidearmSports sites which use the "sidearm" prefix in class names.
  """
  def __init__(self, content):
    self.logger = logging.getLogger("SidearmSportsDgrdProcessor")
    self.content = content

  def clean_text(self, text):
    return ' '.join([s.strip() for s in text.split()])

  def format_hometown_and_state(self, text):
    """Formats text typically in the format "Home town, State".

    Arguments:
      text: The string to format.

    Returns:
      A tuple of the hometown and the state parsed from the provided text.
    """
    if ',' in text:
      hometown, home_state = text.split(',', 1)
      hometown = hometown.strip()
      home_state = home_state.replace(',', '').strip()
    else:
      hometown = text
      home_state = ''
    hometown = self.clean_text(hometown)
    return hometown, home_state

  def format_slash_separated_data(self, text, hs_found=None):
    hometown = home_state = high_school = club = ''
    # The text of this table data usually contains multiple types of information
    # separated by slash characters, "/", e.g.:
    # Hometown, Home State / High School / Previous Schoool / Club Team
    if '/' in text:
      # The might be multiple slashes, but split on the first one for now
      before_slash, after_slash = text.split('/', 1)
      hometown, home_state = self.format_hometown_and_state(before_slash)
      if '/' in after_slash:
        # If there is another slash in the remaining string, it is most likely
        # the high school and club team.
        second_slash, third_slash = after_slash.split('/', 1)
        high_school = self.clean_text(second_slash)
        club = self.clean_text(third_slash)
      else:
        if not hs_found:
          high_school = self.clean_text(after_slash)
        else:
          if after_slash:
            # If the high school was already found and we still had trailing
            # text after the hometown, log it to debug it.
            self.logger.debug('Not sure what this string is: %s', after_slash)
    else:
      # If there is no slash, then the data is most likely just the hometown
      hometown, home_state = self.format_hometown_and_state(text)
    return hometown, home_state, high_school, club

  def get_team(self):
    name = jersey = position = height = hometown = \
        home_state = high_school = year = club = ''
    team = []
    players = self.content.findAll('tr', attrs={'class':
                                                re.compile('^default_dgrd')})
    for player in players:
      if player:
        tds = player.select('td')
        if tds:
          for td in tds:
            if 'class' in td.attrs:
              # class_attrs is a list of string values, so for each class name
              # substring (e.g., the "full_name" substring is used to find the
              # class name "roster_dgrd_full_name"), we need to test if it is in
              # any of the class attribute values list.
              class_attrs = td.attrs['class']
              if any('full_name' in a for a in class_attrs):
                name = self.clean_text(td.get_text())
              elif any('_no' in a for a in class_attrs):
                jersey = self.clean_text(td.get_text())
                if jersey.startswith('#'):
                  jersey = jersey[1:]
              elif any('position' in a for a in class_attrs):
                position = self.clean_text(td.get_text())
              elif any('height' in a for a in class_attrs):
                height = self.clean_text(td.get_text())
              elif any('academic_year' in a for a in class_attrs):
                year = self.clean_text(td.get_text())
              elif any('hometown' in a for a in class_attrs):
                hometown, home_state, high_school, club = \
                    self.format_slash_separated_data(td.get_text(), high_school)
              # Sometimes the "custom" class contains hometown/high school data
              # but other times it contains things like acedemic major. If the
              # hometown has not been found yet and the class contains the
              # "custom" substring, then parse it for hometown data.
              elif not hometown and any('custom' in a for a in class_attrs):
                hometown, home_state, high_school, club = \
                    self.format_slash_separated_data(td.get_text(), high_school)
                # if '/' in td.get_text():
                #   hometown_text = td.get_text()[:td.get_text().find('/')]
                #   high_school_text = td.get_text()[td.get_text().find('/') + 1:]
                #   hometown = hometown_text.strip()
                #   if ',' in hometown:
                #     hometown, home_state = hometown.split(',', 1)
                #     hometown = hometown.strip()
                #     home_state = home_state.replace(',', '').strip()
                #   if not high_school:
                #     high_school = high_school_text.strip()
                # else:
                #   hometown = td.get_text().strip()
                #   if not high_school:
                #     high_school = ''
              elif any('highschool' in a for a in class_attrs):
                high_school = self.clean_text(td.get_text())
              elif any('previous' in a for a in class_attrs):
                club = self.clean_text(td.get_text())
      if name:
        team.append({
          'name': name,
          'jersey': jersey,
          'position': position,
          'height': height,
          'hometown': hometown,
          'home_state': home_state,
          'high_school': high_school,
          'year': year,
          'club': club,
        })
        # Reset the variables
        name = jersey = position = height = hometown = \
            home_state = high_school = year = club = ''
    return team


class SidearmProcessor(object):

  REGEXS = {
    'name': r'.*([a-zA-Z]+\ {1,2}[a-zA-Z]+\ *[a-zA-Z]*).*',
    'jersey-number': r'.*(\d{1,2}).*',
    'position': r'^([a-zA-Z]+).+',
  }

  def __init__(self, content):
    self.logger = logging.getLogger('SidearmProcessor')
    self.content = content

  def SidearmSelectText(self, player, class_substr):
    class_selector = '[class*="%s"]' % class_substr
    nodes = player.select(class_selector)
    text = ''
    if len(nodes):
      node_text = nodes[0].get_text().strip()
      if class_substr in self.REGEXS:
        match = re.search(self.REGEXS[class_substr], node_text)
        if match:
          node_text = match.group()
        else:
          self.logger.warn('No match for: %s', class_substr)
          self.logger.warn('Node text: %s', player.encode('utf-8'))
      text = ' '.join(node_text.split()).strip()
    else:
      self.logger.warn('Node not found for class selector: %s', class_selector)
    return text

  def GetTeamFromSidearmTable(self):
    players = self.content.findAll('li', attrs={'class': 'sidearm-roster-player'})
    name = jersey = position = height = hometown = \
        home_state = high_school = year = club = ''
    team = []
    for player in players:
      name = self.SidearmSelectText(player, 'name')
      jersey = self.SidearmSelectText(player, 'jersey-number')
      # Position is a special case since the 'position' class attribute usually
      # has other elements nested under it. In order to get only the position
      # string we need to get the first <span> child.
      position_element = player.select('[class="text-bold"]')
      if len(position_element):
        for span in position_element[0].children:
          if hasattr(span, 'get_text'):
            position = span.get_text().strip()
            break
      height = self.SidearmSelectText(player, 'height')
      hometown = self.SidearmSelectText(player, 'sidearm-roster-player-hometown')
      if ',' in hometown:
        hometown, home_state = hometown.split(',', 1)
        hometown = hometown.strip()
        home_state = home_state.replace(',', '').strip()
      high_school = self.SidearmSelectText(player, 'sidearm-roster-player-highschool')
      if not high_school:
        high_school = self.SidearmSelectText(player, 'sidearm-roster-player-previous-school')
      year = self.SidearmSelectText(player, 'sidearm-roster-player-academic-year')
      if name:
        team.append({
          'name': name,
          'jersey': jersey,
          'position': position,
          'height': height,
          'hometown': hometown,
          'home_state': home_state,
          'high_school': high_school,
          'year': year,
          'club': club,
        })
    return team


  def get_team(self):
    if self.content.findAll('table',
                            attrs={'class': re.compile('.*default_dgrd.*')}):
      return SidearmSportsDgrdProcessor(self.content).get_team()
    else:
      return self.GetTeamFromSidearmTable()


class SportSelectProcessor(ProcessorBase):
  """Processes roster websites with the SportSelect URL."""

  def __init__(self, content):
    super().__init__(content, 'SportSelectProcessor')

  def get_data_node_text(self, node):
    return node.select('[class="data"]')[0].get_text().strip()

  def get_players(self):
    return self.content.findAll('div',
                                attrs={'class': re.compile('player.+left')})

  def get_player_name(self, player):
    name_text = player.select('[class*="player-name"]')[0].get_text()
    return self.remove_extra_spaces(name_text)

  def get_player_jersey(self, player):
    jersey_text = player.select('[class*="number"]')[0].get_text().strip()
    if jersey_text.startswith('#'):
      jersey = jersey_text[1:]
    else:
      jersey = jersey_text
    return jersey

  def get_player_position(self, player):
    return self.get_data_node_text(player.select('[class*="position"]')[0])

  def get_player_height(self, player):
    return player.select('[class*="height"]')[0].get_text().strip()

  def get_player_year(self, player):
    return self.get_data_node_text(player.select('[class*="year"]')[0])

  def get_hometown_homestate_highschool_club(self, player):
    hometown = home_state = high_school = club = ''
    hometown_text = self.get_data_node_text(
        player.select('[class*="hometown"]')[0])
    # SportSelect sites put the high school name in parenthesis after the
    # hometown name and state. Example: McKinney, Texas (Boyd HS).
    # This regex looks for text plus special characters between parenthesis, as
    # sometimes the high school name is more than letters, e.g., St. John's HS.
    # There is also the potential for multiple listings in parenthesis, such as
    # (previous school) (high school) (club name). Using findall() will get all
    # of these listings in a list.
    sport_select_hs_format =  re.findall(r'(\([a-zA-Z\.\,\s\-\'\&\/^(]+\)*)',
                                         hometown_text)
    if sport_select_hs_format:
      # When there is a previous school that the player transferred from, it is
      # usually listed first, so pop the end of the list for the high school.
      pop_last = sport_select_hs_format.pop()
      high_school = pop_last.replace('(', '').replace(')', '')
      high_school = self.remove_extra_spaces(high_school)
    # If there are still more listings after poping the last one, then either
    # there is a previous school listed or a club team is listed. A previous
    # school listing is less likely so assume a club listing.
    if sport_select_hs_format:
      club = high_school
      pop_again = sport_select_hs_format.pop()
      high_school = pop_again.replace('(', '').replace(')', '')
      high_school = self.remove_extra_spaces(high_school)
    # Get the text up to the first parenthesis if one exists.
    if '(' in hometown_text:
      end_index = hometown_text.index('(') - 1
    else:
      end_index = len(hometown_text)
    hometown = hometown_text[:end_index].strip()
    if ',' in hometown:
      hometown, home_state = hometown.split(',', 1)
      hometown = hometown.strip()
      # Need to remove any extra commas for correct CSV alignment
      home_state = home_state.replace(',', '').strip()
    return hometown, home_state, high_school, club

  def get_team(self):
    players = self.get_players()
    for player in players:
      self.name = self.get_player_name(player)
      self.jersey = self.get_player_jersey(player)
      self.position = self.get_player_position(player)
      self.height = self.get_player_height(player)
      self.year = self.get_player_year(player)
      self.hometown, self.home_state, self.high_school, self.club = \
          self.get_hometown_homestate_highschool_club(player)
      self.add_player_to_team()
    return self.team
