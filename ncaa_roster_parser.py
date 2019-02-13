"""Classes for parsing different types of roster page HTML schemas.

Classes:
  SidearmSportsDgrdProcessor: For processing roster webpages which use CSS class
      names that contain the prefix, "dgrd".
  SidearmSportsSidearmClassNameProcessor: For processing roster webpages which
      use CSS class names which contain the prefix, "sidearm".
  SportSelectProcessor: For processing roster webpages with the SportSelect.aspx
      path name.
  HtmlTableProcessor: Roster webpages with generic HTML tables.
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
  def __init__(self, content, logger_name):
    self.content = content
    self.logger = logging.getLogger(logger_name)
    self.name = ''
    self.jersey = ''
    self.position = ''
    self.height = ''
    self.hometown = ''
    self.home_state = ''
    self.high_school = ''
    self.year = ''
    self.club = ''
    self.team = []

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


class SidearmProcessor(object):
  """Manager class that delegates work to the correct Sidearm processor."""

  def __init__(self, content):
    self.logger = logging.getLogger('SidearmProcessor')
    self.content = content

  def get_team(self):
    # Dgrd-style webpages contain a <table> that uses the default_dgrd class
    # name. If that is not present in the DOM use the regular Sidearm processor.
    if self.content.findAll('table',
                            attrs={'class': re.compile('.*default_dgrd.*')}):
      return SidearmSportsDgrdProcessor(self.content).get_team()
    else:
      return SidearmSportsSidearmClassNameProcessor(self.content).get_team()


class SidearmSportsDgrdProcessor(ProcessorBase):
  """For SidearmSports sites that use the "dgrd" prefix for CSS class names.

  Some roster sites created by SidearmSports use the "dgrd" (I'm assuming this
  stands for "data grid"?) prefix and have a different DOM structure than other
  SidearmSports sites which use the "sidearm" prefix in class names.
  """

  def __init__(self, content):
    super().__init__(content, 'SidearmSportsDgrdProcessor')

  def format_hometown_and_state(self, text):
    """Splits text typically in the format like "Home Town, State".

    Arguments:
      text: The string to format.

    Returns:
      A tuple of the hometown and the state parsed from the provided text.
    """
    if ',' in text:
      hometown, home_state = text.split(',', 1)
      home_state = self.remove_extra_spaces(home_state)
    else:
      hometown = text
      home_state = ''
    hometown = self.remove_extra_spaces(hometown)
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
        high_school = self.remove_extra_spaces(second_slash)
        club = self.remove_extra_spaces(third_slash)
      else:
        if not hs_found:
          high_school = self.remove_extra_spaces(after_slash)
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
    players = self.content.findAll('tr', attrs={'class':
                                                re.compile('^default_dgrd')})
    for player in players:
      if player:
        tds = player.select('td')
        if tds:
          for td in tds:
            if 'class' in td.attrs:
              class_attrs = td.attrs['class']
              # class_attrs is a list of string values, so for each class name
              # substring (e.g., the "full_name" substring is used to find the
              # class name "roster_dgrd_full_name"), we need to test if it is in
              # any of the class attribute values list.
              if any('full_name' in a for a in class_attrs):
                self.name = self.remove_extra_spaces(td.get_text())
              elif any('_no' in a for a in class_attrs):
                jersey = self.remove_extra_spaces(td.get_text())
                if jersey.startswith('#'):
                  self.jersey = jersey[1:]
                else:
                  self.jersey = jersey
              elif any('position' in a for a in class_attrs):
                self.position = self.remove_extra_spaces(td.get_text())
              elif any('height' in a for a in class_attrs):
                self.height = self.remove_extra_spaces(td.get_text())
              elif any('academic_year' in a for a in class_attrs):
                self.year = self.remove_extra_spaces(td.get_text())
              elif any('hometown' in a for a in class_attrs):
                self.hometown, self.home_state, self.high_school, self.club = \
                    self.format_slash_separated_data(td.get_text(),
                                                     self.high_school)
              # Sometimes the "custom" class contains hometown/high school data
              # but other times it contains things like acedemic major. If the
              # hometown has not been found yet and the class contains the
              # "custom" substring, then parse it for hometown data.
              elif not self.hometown and any('custom' in a for a in class_attrs):
                self.hometown, self.home_state, self.high_school, self.club = \
                    self.format_slash_separated_data(td.get_text(),
                                                     self.high_school)
              elif any('highschool' in a for a in class_attrs):
                self.high_school = self.remove_extra_spaces(td.get_text())
              elif any('previous' in a for a in class_attrs):
                self.club = self.remove_extra_spaces(td.get_text())
      self.add_player_to_team()
    return self.team


class SidearmSportsSidearmClassNameProcessor(ProcessorBase):
  """For Sidearm Sports roster pages that use "sidearm" in div class names."""

  def __init__(self, content):
    super().__init__(content, 'SidearmSportsSidearmClassNameProcessor')

  def get_player_name(self, player):
    class_selector = '[class="sidearm-roster-player-name"]'
    nodes = player.select(class_selector)
    if nodes:
      node_text = nodes[0].get_text()
      m = re.search('[a-zA-Z]', node_text)
      if m:
        name = node_text[m.start():]
        return self.remove_extra_spaces(name)
      else:
        self.logger.warning('Could not find player name in this node text: %s',
                            node_text)
    else:
      self.logger.warning('Node not found for class selector: %s',
                          class_selector)
      self.logger.warning('Player HTML: %s', str(player))
    return ''  # After any logging scenario return empty string.

  def get_player_jersey(self, player):
    class_selector = '[class="sidearm-roster-player-jersey-number"]'
    nodes = player.select(class_selector)
    if nodes:
      return self.remove_extra_spaces(nodes[0].get_text())
    else:
      self.logger.warning('Node not found for class selector: %s',
                          class_selector)
      self.logger.warning('Player HTML: %s', str(player))
    return ''  # After any logging scenario return empty string.

  def get_player_position(self, player):
    # Position exists in the DOM in 2 versions, a long version (e.g. "Forward"),
    # and a short version (e.g., "F"). We want the short version, which is
    # differentiated by having the "hide-on-medium" CSS style.
    position_node = player.select('span'
                                  '.sidearm-roster-player-position-long-short'
                                  '.hide-on-medium')
    return self.remove_extra_spaces(position_node[0].get_text())

  def get_player_height(self, player):
    class_selector = '[class="sidearm-roster-player-height"]'
    nodes = player.select(class_selector)
    if nodes:
      return self.remove_extra_spaces(nodes[0].get_text())
    else:
      self.logger.warning('Node not found for class selector: %s',
                          class_selector)
      self.logger.warning('Player HTML: %s', str(player))
    return ''  # After any logging scenario return empty string.

  def get_player_hometown_and_home_state(self, player):
    class_selector = '[class="sidearm-roster-player-hometown"]'
    nodes = player.select(class_selector)
    if nodes:
      node_text = nodes[0].get_text()
      if ',' in node_text:
        hometown, home_state = node_text.split(',', 1)
        hometown = self.remove_extra_spaces(hometown)
        home_state = self.remove_extra_spaces(home_state)
      else:
        hometown = self.remove_extra_spaces(node_text)
        home_state = ''
      return hometown, home_state
    else:
      self.logger.warning('Node not found for class selector: %s',
                          class_selector)
      self.logger.warning('Player HTML: %s', str(player))
    return ('', '')  # After any logging scenario return empty string.

  def get_player_high_school(self, player):
    class_selector = '[class="sidearm-roster-player-highschool"]'
    nodes = player.select(class_selector)
    if nodes:
      return self.remove_extra_spaces(nodes[0].get_text())
    else:
      self.logger.warning('Node not found for class selector: %s',
                          class_selector)
      self.logger.warning('Player HTML: %s', str(player))
      # Sometimes the high school name is listed in a node with the class name,
      # "previous-school". So if we didn't find a high school, try this
      # alternative.
      class_selector = '[class="sidearm-roster-player-previous-school"]'
      nodes = player.select(class_selector)
      if nodes:
        return self.remove_extra_spaces(nodes[0].get_text())
      else:
        self.logger.warning('Node not found for class selector: %s',
                            class_selector)
        self.logger.warning('Player HTML: %s', str(player))
    return ''  # After any logging scenario return empty string.

  def get_player_year(self, player):
    class_selector = '[class="sidearm-roster-player-academic-year"]'
    nodes = player.select(class_selector)
    if nodes:
      return self.remove_extra_spaces(nodes[0].get_text())
    else:
      self.logger.warning('Node not found for class selector: %s',
                          class_selector)
      self.logger.warning('Player HTML: %s', str(player))
    return ''  # After any logging scenario return empty string.

  def get_player_club(self, player):
    class_selector = '[class="sidearm-roster-player-custom1"]'
    nodes = player.select(class_selector)
    if nodes:
      return self.remove_extra_spaces(nodes[0].get_text())
    else:
      return ''  # After any logging scenario return empty string.

  def get_team(self):
    players = self.content.findAll('li',
                                   attrs={'class': 'sidearm-roster-player'})
    for player in players:
      self.name = self.get_player_name(player)
      self.jersey = self.get_player_jersey(player)
      self.position = self.get_player_position(player)
      self.height = self.get_player_height(player)
      self.hometown, self.home_state = \
          self.get_player_hometown_and_home_state(player)
      self.year = self.get_player_year(player)
      self.club = self.get_player_club(player)
      self.add_player_to_team()
    return self.team


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


class HtmlTableProcessor(ProcessorBase):
  """Parses roster webpages with generic HTML tables."""

  def __init__(self, content):
    super().__init__(content, 'HtmlTableProcessor')

  def get_players(self):
    # Each table row is a different roster player.
    return self.content.findAll('tr')

  def get_player_name(self, player):
    th = player.select('th')
    if th:
      return self.remove_extra_spaces(th[0].get_text())

  def get_labels_and_data(self, player):
    """Extract label/data pairs from table data nodes.

    Each <td> node is formated with a child <span> node that has a class name of
    "label", where the inner text contains the label (e.g., position, class,
    etc.) and the inner text of the <td> (outside of the <span> contains the
    data value (e.g., GK, Freshman, etc.). Here we extract both the label and
    the data value. Example node:
      <td>
        <span class="label">
          Pos.:
        </span>
        Defender
      </td>
    """
    labels_and_data = {}
    tds = player.select('td')
    for td in tds:
      data_text = td.get_text().strip()
      label_text = None
      spans = td.select('span')
      for span in spans:
        if span.attrs and 'label' in list(span.attrs.values())[0]:
          label_text = span.get_text().strip()
      # Since the <span> text will be included in the <td> text it needs to be
      # removed.
      data_text = data_text.replace(label_text, '')
      if 'hometown' in label_text.lower():
        label_texts = label_text.split('/')
        data_texts = data_text.split('/')
        for i, label in enumerate(label_texts):
          try:
            if 'hometown' in label.lower() and ',' in data_texts[i]:
              hometown, home_state = data_texts[i].split(',', 1)
              labels_and_data['hometown'] = self.remove_extra_spaces(hometown)
              labels_and_data['state'] = self.remove_extra_spaces(home_state)
            else:
              label = self.remove_extra_spaces(label)
              data = self.remove_extra_spaces(data_texts[i])
          except IndexError:
            self.logger.error(
              'Labels and data do not match. Labels: %s, Data: %s',
              label_texts,
              data_texts)
          # Lowercase all labels so they are easier to match.
          label = label.lower()
          # The "Hometown" label can go through this loop twice, so if we
          # already have its value, don't overwrite it.
          if label not in labels_and_data:
            labels_and_data[label] = data
      else:
        label = self.remove_extra_spaces(label_text)
        data = self.remove_extra_spaces(data_text)
        # Lowercase all labels so they are easier to match.
        label = label.lower()
        labels_and_data[label] = data
    return labels_and_data

  def get_team(self):
    players = self.get_players()
    for player in players:
      labels_and_data = self.get_labels_and_data(player)
      # If all of the values we got back are empty, then we can ignore. Only
      # record this player if there is at least one value returned.
      if any(labels_and_data.values()):
        self.name = self.get_player_name(player)
        for label, data in labels_and_data.items():
          if 'no' in label:
            self.jersey = data
          elif 'pos' in label:
            self.position = data
          elif any(x in label for x in ['yr', 'year', 'cl.', 'class']):
            self.year = data
          elif any(x in label for x in ['ht', 'height']):
            self.height = data
          elif 'hometown' in label:
            self.hometown = data
          elif 'state' in label:
            self.home_state = data
          elif any(x in label for x in ['high', 'prev', 'last']):
            self.high_school = data
          elif 'club' in label:
            self.club = data
          else:
            self.logger.debug('Could not find specifier for label: %s', label)
        self.add_player_to_team()
    return self.team
