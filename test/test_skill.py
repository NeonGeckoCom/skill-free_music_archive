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

import pytest

from ovos_plugin_common_play import MediaType
from neon_minerva.tests.skill_unit_test_base import SkillTestCase


class TestSkillMethods(SkillTestCase):
    def test_00_skill_init(self):
        # Test any parameters expected to be set in init or initialize methods
        from ovos_workshop.skills.common_play import OVOSCommonPlaybackSkill

        self.assertIsInstance(self.skill, OVOSCommonPlaybackSkill)
        self.assertIsInstance(self.skill._base_url, str)
        self.assertIsInstance(self.skill._image_url, str)

    def test_query_url(self):
        # Test simple URL
        url = self.skill.query_url("test")
        self.assertIn("test", url)
        self.assertTrue(url.startswith(self.skill._base_url))

        # Test multi-word search
        url = self.skill.query_url("two word test")
        self.assertTrue(url.startswith(self.skill._base_url))
        self.assertIn("two%20word%20test", url)

    def test_search_songs(self):
        songs = self.skill._search_songs("jazz")
        self.assertIsInstance(songs, list)
        for s in songs:
            self.assertIsInstance(s, dict)
            self.assertIsInstance(s['playbackUrl'], str)
            self.assertIsInstance(s['title'], str)
            self.assertIsInstance(s['artistName'], str)

    def test_search_fma(self):
        # Simple search
        results = self.skill.search_fma("jazz", MediaType.MUSIC)
        self.assertIsInstance(results, list)
        self.assertTrue(results)
        for r in results:
            self.assertIsInstance(r, dict)
            self.assertGreaterEqual(r['match_confidence'], 15)

        # Remove articles search
        results = self.skill.search_fma("some jazz", MediaType.MUSIC)
        self.assertIsInstance(results, list)
        self.assertTrue(results)
        for r in results:
            self.assertIsInstance(r, dict)
            self.assertGreaterEqual(r['match_confidence'], 10)

        # Genre search
        results = self.skill.search_fma("jazz song", MediaType.MUSIC)
        self.assertIsInstance(results, list)
        self.assertTrue(results)
        for r in results:
            self.assertIsInstance(r, dict)
            self.assertGreaterEqual(r['match_confidence'], 15)


if __name__ == '__main__':
    pytest.main()
