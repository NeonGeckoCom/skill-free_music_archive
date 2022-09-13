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
import requests

from bs4 import BeautifulSoup
from ovos_plugin_common_play import MediaType, PlaybackType
from ovos_workshop.skills.common_play import OVOSCommonPlaybackSkill, \
    ocp_search


class FreeMusicArchiveSkill(OVOSCommonPlaybackSkill):
    def __init__(self):
        super(FreeMusicArchiveSkill, self).__init__()
        self._base_url = "https://freemusicarchive.org/search?adv=1" \
                         "&music-filter-CC-attribution-only=1" \
                         "&music-filter-CC-attribution-sharealike=1" \
                         "&music-filter-CC-attribution-noderivatives=1" \
                         "&music-filter-public-domain=1" \
                         "&music-filter-commercial-allowed=1"

    def query_url(self, search_term: str):
        return f'{self._base_url}&quicksearch={search_term}&&&'

    @ocp_search()
    def search_fma(self, phrase, media_type=MediaType.GENERIC):
        score = 0
        if media_type == MediaType.MUSIC:
            score += 15
        songs = [json.loads(song['data-track-info']) for song in
                 BeautifulSoup(requests.get(self.query_url(phrase)).content)
                 .find_all('div', class_='play-item gcol gid-electronic')]
        score += max(len(songs), 50)
        results = [{'media_type': MediaType.AUDIO,
                    'playback': PlaybackType.AUDIO,
                    'uri': song['playbackUrl'],
                    'title': song['title'],
                    'artist': song['artistName'],
                    'match_confidence': score,
                    } for song in songs]
        return results


def create_skill():
    return FreeMusicArchiveSkill()
