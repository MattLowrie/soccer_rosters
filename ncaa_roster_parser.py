"""Classes for parsing different roster page HTML schemas.

Classes:
  HtmlTableProcessor: For generic HTML tables.
"""
import logging
import re
from bs4 import BeautifulSoup as bs


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


class SportSelectProcessor(object):

  def __init__(self, content):
    self.logger = logging.getLogger('SportSelectProcessor')
    self.content = content

  def get_team(self):
    name = jersey = position = height = hometown = home_state = high_school = year = club = ''
    team = []
    players = self.content.findAll('div', attrs={'class': re.compile('player.+left')})
    for player in players:
      name_text = player.select('[class*="player-name"]')[0].get_text().strip()
      name = ' '.join(name_text.split())
      jersey_text = player.select('[class*="number"]')[0].get_text().strip()
      if jersey_text.startswith('#'):
        jersey = jersey_text[1:]
      else:
        jersey = jersey_text
      height = player.select('[class*="height"]')[0].get_text().strip()
      position = player.select('[class*="position"]')[0].select('[class="data"]')[0].get_text().strip()
      year = player.select('[class*="year"]')[0].select('[class="data"]')[0].get_text().strip()
      hometown_text = player.select('[class*="hometown"]')[0].select('[class="data"]')[0].get_text().strip()
      # SportSelect sites put the high school name in parenthesis after the hometown
      # name and state.
      sport_select_hs_format =  re.findall('(\([a-zA-Z\.\,\s\-^(]+\)*)', hometown_text)
      if sport_select_hs_format:
        high_school = sport_select_hs_format[-1]
        if high_school.startswith('(') and high_school.endswith(')'):
          high_school = high_school[1:-1]
      else:
        high_school = ''
      hometown = hometown_text[:hometown_text.find('(') -1].strip()
      if ',' in hometown:
        hometown, home_state = hometown.split(',', 1)
        hometown = hometown.strip()
        home_state = home_state.replace(',', '').strip()
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
