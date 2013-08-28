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
for li in soup.findAll('li')[1:]: #  skip header row
    show = {}

    # show title and link
    col_title = li.find('span', class_='col_tit')
    if col_title is None:
        continue
    a_title = col_title.find('a')
    show['title'] = a_title.text
    show['link'] = 'http://www.rtve.es/' + a_title.attrs['href']

    # audio (mp3) url
    col_audio = li.find('span', class_='col_tip')
    if col_audio:
        a = col_audio.find('a')
        if a is None:
            continue
        show['audio'] = a.attrs['href']

    # show duration
    col_duration = li.find('span', class_='col_dur')
    if col_duration is None:
        continue
    show['duration'] = col_duration.text

    # show popularity however this is measured
    col_popularity = li.find('span', class_='col_pop')
    if col_popularity is None:
        continue
    show['popularity'] = col_popularity.text

    shows.append(show)

# create reStructuredText
doc = rst.Document('Rock Reaktor Archive')
table = rst.Table('All shows', ['Title', 'Duration', 'Popularity'])

for show in shows:
    table.add_item(
        ('`%s <%s>`_' % (show['title'], show['link']),
         '`%s <%s>`_' % (show['duration'], show['audio']),
         show['popularity'])
    )

doc.add_child(table)
with open('README.rst', 'w') as f:
    f.write(doc.get_rst().encode('utf-8'))