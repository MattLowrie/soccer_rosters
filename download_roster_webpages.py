import argparse
import brotli
from bs4 import BeautifulSoup as bs
import csv
import logging
import requests
import sys
from urllib.parse import urlparse
from urllib.parse import urlunparse

from util import roster_file_util


# The roster web servers only return a response if the request headers simulate
# a real web browser.
HTTP_HEADERS = {
  'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36',
  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
  'Accept-Encoding': 'gzip, deflate, br',
  'Accept-Language': 'en-US,en;q=0.9'
}


def format_request_args(urls):
  """Formats URLs for the requests module.

  This routine parses every roster URL and formats it as a dict of function
  arguments to pass to requests.get(). Also cleans up some query strings.

  Arguments:
    urls: A list of strings of every roster url.

  Returns:
    A 2-tuple:
        First a list of dicts of request args to pass into requests.get().
        Second a list of string of urls with corrected query params.
  """
  request_args = []
  corrected_urls = []
  for url in urls:
    parsed_url = urlparse(url)
    params = {}
    if parsed_url.query:
      query_params = parsed_url.query.split('&')
      for query_param in query_params:
        if '=' in query_param:
          k, v = query_param.split('=')
          # SidearmSports sites use the "path=" query param to designate which
          # school sport to display. For women's soccer, valid values for this
          # param can be, "wsoc", "wsoccer", "soc", or ""<empty string>"". Since
          # the URLs are found using Google results, the school website URL may
          # be correct, but the "path=" param is pointing to the wrong sport.
          # For our case, we explicitly set the "path=" value to get the women's
          # soccer roster.
          if k == 'path' and v and 'soc' not in v:
            params[k] = 'wsoc'
          else:
            params[k] = v
        else:
          params[query_param] = ''
    reconstituted_url = urlunparse((
      parsed_url.scheme,
      parsed_url.netloc,
      parsed_url.path,
      None, None, None
    ))
    request_args.append({
      'url': reconstituted_url,
      'params': params,
      'headers': HTTP_HEADERS,
    })
    corrected_urls.append(
      urlunparse((
        parsed_url.scheme,
        parsed_url.netloc,
        parsed_url.path,
        None,
        '&'.join(['%s=%s' % (k, v) for k, v in params.items()]),
        None,
      ))
    )
  return request_args, corrected_urls


def get_webpage_content(request_args):
  """Calls each roster URL and returns the content as a BeautifulSoup instance.

  Arguments:
    request_args: A list of dicts that contain the named arguments for the
        function requests.get().

  Returns:
    A list of BeautifulSoup instances, one for each set of request args, unless
        there was an exception with the URL response, in which case the index
        in the instance list will contain an empty string.
  """
  soups = []
  for req_args in request_args:
    try:
      r = requests.get(**req_args)
      if r.status_code == 200:
        if ('Content-encoding' in r.headers and
            r.headers['Content-Encoding'] == 'br'):
          soups.append(bs(brotli.decompress(r.content), 'html.parser'))
        else:
          soups.append(bs(r.content, 'html.parser'))
      else:
        logger.error('Status code %d for %s', r.status_code, req_args['url'])
        logger.error('HTTP reason: %s', r.reason)
        logger.error('HTTP response headers:')
        logger.error(r.raw.getheaders())
        # Keep the length of the content list equal to the URL list
        soups.append('')
    except requests.exceptions.ConnectionError:
      logger.error('Connection error for: %s', req_args['url'])
      # Keep the length of the content list equal to the URL list
      soups.append('')
  return soups


def save_files(soups, schools, corrected_urls, output_dir):
  """Save files locally.

  This function saves 2 files for each school. One containing the HTML content
  of the roster page, and one containing the URL used to request the page.

  Arguments:
    soups: A list of BeaufitfulSoup instances, one for each corresponding
        school in the list of schools.
    schools: A list of strings of each school name.
    corrected_urls: A list of strings of each corresponding school roster URL.
  """
  # Now save each webpage to a local file.
  for i, soup in enumerate(soups):
    file_name = schools[i].replace(' ', '_')
    roster_file_util.write_file(file_name + '.webpage',
                                soup.prettify(),
                                dir_path=output_dir)
    roster_file_util.write_file(file_name + '.url',
                                corrected_urls[i],
                                dir_path=output_dir)


def main():
  logger = logging.getLogger(__name__)

  school_filter = []
  if flags.schools:
    school_filter = [f.strip() for f in flags.schools.split(',')]

  schools, _, _, _, _, _, urls = \
      roster_file_util.read_school_info_file(flags.input_file, school_filter)

  request_args, corrected_urls = format_request_args(urls)

  soups = get_webpage_content(request_args)

  save_files(soups, schools, corrected_urls, flags.output_dir)


def _set_arguments():
  parser = argparse.ArgumentParser()
  parser.add_argument('-i', '--input_file', metavar='FILENAME',
                      default='csv/ncaa_d1_womens_soccer_programs.csv',
                      help='CSV file to read school information in from.')
  parser.add_argument('-o', '--output_dir', metavar='FILENAME',
                      default='roster_webpages',
                      help='The directory to save all webpage files into.'
                        'The directory is relative to the current working'
                        'directory.')
  parser.add_argument('--schools', metavar='"SCHOOL 1, SCHOOL 2, SCHOOL 3"',
                      help='A comma-separated list of schools to output.')
  return parser.parse_args()


if __name__ == '__main__':
  flags = _set_arguments()
  logging.basicConfig(
    filename='/tmp/download_roster_webpages.log',
    filemode='w',
    format= '%(asctime)s,%(msecs)-3d %(levelname)-8s %(filename)s %(name)s - %(message)s',
    datefmt='%m-%d %H:%M:%S',
    level=logging.DEBUG)
  main()
