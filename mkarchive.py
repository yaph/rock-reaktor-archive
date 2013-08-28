#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Create a reStructuredText document that lists all Rock Reaktor shows including
# title, length, show page and download links.

import requests
import requests_cache

from bs4 import BeautifulSoup, SoupStrainer
from rst import rst

# cache requests for one week
requests_cache.install_cache('cache', expire_after=604800)
start_url = 'http://www.rtve.es/alacarta/interno/contenttable.shtml?pbq=1&locale=es&pageSize=348&ctx=22333'
html = requests.get(start_url).text

# use html.parser since default parser may fail
soup = BeautifulSoup(html, 'html.parser',
    parse_only=SoupStrainer(class_='ContentTabla'))

shows = []
show_list = soup.find('ul')
# only immediate child elements
records = show_list.find_all('li', recursive=False)
for li in records[1:]: #  skip header row
    show = {}

    # show title and link
    col_title = li.find('span', class_='col_tit')
    a_title = col_title.find('a')
    show['title'] = a_title.text
    show['link'] = 'http://www.rtve.es' + a_title.get('href', '')

    # audio (mp3) url
    show['audio'] = None
    col_audio = li.find('span', class_='col_tip')
    a = col_audio.find('a')
    if a:
        show['audio'] = a.attrs.get('href', '')

    # show duration
    col_duration = li.find('span', class_='col_dur')
    show['duration'] = col_duration.text

    # show popularity however this is measured
    col_popularity = li.find('span', class_='col_pop')
    show['popularity'] = col_popularity.text

    # show date
    col_date = li.find('span', class_='col_fec')
    show['date'] = col_date.text

    shows.append(show)

# create reStructuredText
doc = rst.Document('Rock Reaktor Archive')
table = rst.Table(
    'All `Rock Reaktor <http://www.rtve.es/alacarta/audios/rock-reaktor/>`_ shows',
    ['#', 'Episode title', 'Duration', 'Popularity', 'Date'])

episode = len(shows)
for show in shows:
    if show['audio']:
        col_audio = '`%s <%s>`_' % (show['duration'], show['audio'])
    else:
        col_audio = show['duration']
    table.add_item(
        ('%d' % episode,
         '`%s <%s>`_' % (show['title'], show['link']),
         col_audio,
         show['popularity'],
         show['date']))
    episode -= 1

doc.add_child(table)
with open('README.rst', 'w') as f:
    f.write(doc.get_rst().encode('utf-8'))