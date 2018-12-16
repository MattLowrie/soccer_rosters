import logging
import re
from bs4 import BeautifulSoup as bs


class TableProcessor(object):

  def __init__(self, content):
    self.logger = logging.getLogger('TableProcessor')
    self.content = content

  def GetTeam(self):
    name = jersey = position = height = hometown = high_school = year = club = ''
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
          datas = slash_split.split(data_text)
          for i, data in enumerate(datas):
            label = ''
            try:
              label = labels[i].strip()
            except IndexError:
              self.logger.error(
                'labels[%d] != datas[%d]', len(labels), len(datas))
              self.logger.debug(labels)
              self.logger.debug(datas)
            data = ' '.join(data.split())
            if True in [x in label for x in ['No']]:
              jersey = data
            elif True in [x in label for x in ['Pos']]:
              position = data
            elif True in [x in label for x in ['Yr', 'Cl', 'Year']]:
              year = data
            elif True in [x in label for x in ['Hometown']]:
              hometown = data
            elif True in [x in label for x in ['High', 'Prev']]:
              high_school = data
            elif True in [x in label for x in ['Ht', 'Height']]:
              height = data
            else:
              self.logger.debug('Could not find specifier for label: %s', label)
      if name:
        team.append({
          'name': name,
          'jersey': jersey,
          'position': position,
          'height': height,
          'hometown': hometown,
          'high_school': high_school,
          'year': year,
          'club': club,
        })
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

  def GetTeam(self):
    players = self.content.findAll('li', attrs={'class': 'sidearm-roster-player'})
    name = jersey = position = height = hometown = high_school = year = club = ''
    team = []
    for player in players:
      name = self.SidearmSelectText(player, 'name')
      jersey = self.SidearmSelectText(player, 'jersey-number')
      position = self.SidearmSelectText(player, 'position')
      height = self.SidearmSelectText(player, 'height')
      hometown = self.SidearmSelectText(player, 'sidearm-roster-player-hometown')
      high_school = self.SidearmSelectText(player, 'sidearm-roster-player-highschool')
      year = self.SidearmSelectText(player, 'sidearm-roster-player-academic-year')
      team.append({
        'name': name,
        'jersey': jersey,
        'position': position,
        'height': height,
        'hometown': hometown,
        'high_school': high_school,
        'year': year,
        'club': club,
      })
    return team
