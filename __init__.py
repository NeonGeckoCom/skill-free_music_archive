# NEON AI (TM) SOFTWARE, Software Development Kit & Application Framework
# All trademark and other rights reserved by their respective owners
# Copyright 2008-2022 Neongecko.com Inc.
# Contributors: Daniel McKnight, Guy Daniels, Elon Gasper, Richard Leeds,
# Regina Bloomstine, Casimiro Ferreira, Andrii Pernatii, Kirill Hrymailo
# BSD-3 License
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from this
#    software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS  BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
# OR PROFITS;  OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE,  EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import json
from typing import List

import requests

from urllib.parse import quote
from bs4 import BeautifulSoup
from neon_utils.file_utils import load_commented_file
from ovos_plugin_common_play import MediaType, PlaybackType
from ovos_workshop.skills.common_play import OVOSCommonPlaybackSkill, \
    ocp_search
from ovos_utils.log import LOG


class FreeMusicArchiveSkill(OVOSCommonPlaybackSkill):
    def __init__(self):
        super(FreeMusicArchiveSkill, self).__init__()
        self.supported_media = [MediaType.MUSIC,
                                MediaType.AUDIO,
                                MediaType.GENERIC]
        self._base_url = "https://freemusicarchive.org/search?adv=1" \
                         "&music-filter-CC-attribution-only=1" \
                         "&music-filter-CC-attribution-sharealike=1" \
                         "&music-filter-CC-attribution-noderivatives=1" \
                         "&music-filter-public-domain=1" \
                         "&music-filter-commercial-allowed=1"
        self._image_url = "https://freemusicarchive.org/legacy/fma-smaller.jpg"

    def query_url(self, search_term: str) -> str:
        """
        Build a query URL for the specified query
        :param search_term: phrase to search
        :returns: str URL to query for results
        """
        return f'{self._base_url}&quicksearch={quote(search_term)}&&&'

    def _search_songs(self, phrase) -> List[dict]:
        """
        Get a list of songs for the specified search phrase
        :param phrase: phrase to search
        :returns: list of dict song information
        """
        return [json.loads(song['data-track-info']) for song in
                BeautifulSoup(requests.get(self.query_url(phrase)).content)
                .find_all('div', class_='play-item gcol gid-electronic')]

    @ocp_search()
    def search_fma(self, phrase, media_type=MediaType.GENERIC) -> List[dict]:
        """
        OCP Search handler to return results for a user request
        :param phrase: search phrase from user
        :param media_type: user requested media type
        :returns: list of dict search results
        """
        score = 0
        if media_type == MediaType.MUSIC:
            score += 15
        songs = self._search_songs(phrase)
        if not songs:
            self.extend_timeout(1)
            # Nothing matched, try removing articles
            LOG.info(f"Trying search with articles removed")
            articles_voc = self.find_resource("articles.voc", lang=self.lang)
            articles = load_commented_file(articles_voc).split('\n')
            cleaned_phrase = ' '.join((word for word in phrase.split()
                                       if word not in articles))
            score -= 5
            songs = self._search_songs(cleaned_phrase)
        if not songs:
            self.extend_timeout(1)
            LOG.info(f"Trying search by genre")
            # Nothing matched, try parsing a genre
            genres_voc = self.find_resource("genre.voc", lang=self.lang)
            genres = load_commented_file(genres_voc).split('\n')
            for g in genres:
                if g in phrase:
                    score += 5
                    songs = self._search_songs(g)
                    break

        score += max(len(songs), 50)
        results = [{'media_type': MediaType.MUSIC,
                    'playback': PlaybackType.AUDIO,
                    'image': self._image_url,
                    'skill_icon': self._image_url,
                    'uri': song['playbackUrl'],
                    'title': song['title'],
                    'artist': song['artistName'],
                    'match_confidence': score,
                    } for song in songs]
        LOG.info(f"Returning {len(results)} results with confidence {score}")
        return results


def create_skill():
    return FreeMusicArchiveSkill()
