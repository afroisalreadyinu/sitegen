import unittest
import tempfile
from pathlib import Path

import feedparser

from sitegen.content import ContentFile, ContentContext
from sitegen import feeds

from common import FakeTemplates, FakeTemplate, CollectionTestBase

class ContentContextTests(unittest.TestCase, CollectionTestBase):

    def setUp(self):
        self.workdir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.workdir.cleanup()

    def test_generate_feed(self):
        context = ContentContext()
        contents = [self.make_content_file('blog', 'the-entry', 'The Entry'),
                    self.make_content_file('tutorial', 'the-tutorial', 'The Tutorial'),
                    self.make_content_file('litany', 'the-litany', 'The Litany')]
        feed_xml = feeds.generate_feed({'site': {'title': 'Test Site', 'url': 'https://bb.com', 'author': 'U T'}},
                                       contents)
        feed = feedparser.parse(feed_xml)['feed']
        assert feed['title'] == "Test Site RSS Feed"
