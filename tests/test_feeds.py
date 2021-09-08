import unittest
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

import feedparser

from sitegen.feeds import FeedGenerator

from common import FakeTemplates, FakeTemplate, CollectionTestBase

CONFIG = {'site': {'title': 'Test Site', 'url': 'https://bb.com', 'author': 'U T', 'locale': 'en-US'}}

class FeedTests(unittest.TestCase, CollectionTestBase):

    def setUp(self):
        self.workdir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.workdir.cleanup()

    def test_generate_feed(self):
        fg = FeedGenerator()
        fg.append_content_file(self.make_content_file('blog', 'the-entry', 'The Entry'))
        fg.append_content_file(self.make_content_file('tutorial', 'the-tutorial', 'The Tutorial'))
        fg.append_content_file(self.make_content_file('litany', 'the-litany', 'The Litany'))
        feed_xml = fg.generate_feed(CONFIG)
        parsed = feedparser.parse(feed_xml)
        assert parsed.feed.title == "Test Site RSS Feed"
        assert parsed.feed.description == "RSS Feed for Test Site"
        assert parsed.feed.link == "https://bb.com/rss.xml"
        assert parsed.feed.language == "en-US"
        assert len(parsed.entries) == 3
        titles = set(x.title for x in parsed.entries)
        assert titles == set(['The Litany', 'The Tutorial', 'The Entry'])

    def test_entry_details(self):
        fg = FeedGenerator()
        fg.append_content_file(self.make_content_file('blog', 'the-entry', 'The Entry'))
        feed_xml = fg.generate_feed(CONFIG)
        parsed = feedparser.parse(feed_xml)
        assert len(parsed.entries) == 1
        entry = parsed.entries[0]
        assert entry.title == 'The Entry'
        assert entry.link == 'https://bb.com/blog/the-entry'
        assert entry.author == 'U T'

    def test_order_by_date(self):
        fg = FeedGenerator()
        now = datetime.now().replace(second=0, microsecond=0)
        # Let's insert these out of order
        fg.append_content_file(self.make_content_file('litany', 'the-litany', 'The Litany',
                                                      date=now - timedelta(hours=1)))
        fg.append_content_file(self.make_content_file('blog', 'the-entry', 'The Entry',
                                                      date=now + timedelta(hours=1)))
        fg.append_content_file(self.make_content_file('tutorial', 'the-tutorial', 'The Tutorial', date=now))
        feed_xml = fg.generate_feed(CONFIG)
        parsed = feedparser.parse(feed_xml)
        assert parsed.entries[0].title == 'The Entry'
        assert parsed.entries[1].title == 'The Tutorial'
        assert parsed.entries[2].title == 'The Litany'

    def test_skip_index(self):
        fg = FeedGenerator()
        now = datetime.now().replace(second=0, microsecond=0)
        fg.append_content_file(self.make_content_file('blog', 'the-entry', 'The Entry'))
        fg.append_content_file(self.make_content_file('', 'index', ''))
        feed_xml = fg.generate_feed(CONFIG)
        parsed = feedparser.parse(feed_xml)
        assert len(parsed.entries) == 1
        assert parsed.entries[0].title == 'The Entry'

    def test_render(self):
        fg = FeedGenerator()
        now = datetime.now().replace(second=0, microsecond=0)
        # Let's insert these out of order
        fg.append_content_file(self.make_content_file('litany', 'the-litany', 'The Litany',
                                                      date=now - timedelta(hours=1)))
        fg.append_content_file(self.make_content_file('blog', 'the-entry', 'The Entry',
                                                      date=now + timedelta(hours=1)))
        fg.append_content_file(self.make_content_file('tutorial', 'the-tutorial', 'The Tutorial', date=now))
        public_dir = Path(self.workdir.name) / 'public'
        fg.render(CONFIG, str(public_dir))
        with open(public_dir / 'rss.xml', 'r') as feed_file:
            feed_xml = feed_file.read()
        parsed = feedparser.parse(feed_xml)
        assert parsed.feed.title == "Test Site RSS Feed"
        assert len(parsed.entries) == 3
