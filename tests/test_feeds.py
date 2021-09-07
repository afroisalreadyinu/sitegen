import unittest
import tempfile
from pathlib import Path

import feedparser

from sitegen.feeds import FeedGenerator

from common import FakeTemplates, FakeTemplate, CollectionTestBase

class ContentContextTests(unittest.TestCase, CollectionTestBase):

    def setUp(self):
        self.workdir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.workdir.cleanup()

    def test_generate_feed(self):
        fg = FeedGenerator()
        fg.append_content_file(self.make_content_file('blog', 'the-entry', 'The Entry'))
        fg.append_content_file(self.make_content_file('tutorial', 'the-tutorial', 'The Tutorial'))
        fg.append_content_file(self.make_content_file('litany', 'the-litany', 'The Litany'))
        feed_xml = fg.generate_feed({'site': {'title': 'Test Site', 'url': 'https://bb.com', 'author': 'U T'}})
        parsed = feedparser.parse(feed_xml)
        assert parsed.feed.title == "Test Site RSS Feed"
        assert len(parsed.entries) == 3
        assert 'The Litany' in [x.title for x in parsed.entries]
