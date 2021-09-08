import os
import unittest
from types import SimpleNamespace as Bunch
import tempfile
from datetime import datetime, timedelta

from sitegen.content import Section, PageContent, SiteInfo
from common import FakeTemplate, FakeTemplates, CollectionTestBase

CONFIG = {'site': {'url': 'http://bb.com', 'title': 'HELLO'}}

class SectionTests(unittest.TestCase, CollectionTestBase):

    def setUp(self):
        self.workdir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.workdir.cleanup()

    def test_get_context(self):
        section = Section('blog')
        high_date = datetime.now().replace(second=0, microsecond=0) + timedelta(hours=1)
        section.append_content_file(self.make_content_file('blog', 'the-entry', 'The Entry', date=high_date))
        section.append_content_file(self.make_content_file('blog', 'other-entry', 'Other Entry'))
        context = section.get_context(CONFIG)
        assert 'items' in context
        assert len(context.pop('items')) == 2
        assert context['page_content'] == PageContent(title='blog',
                                                      description='',
                                                      canonical_url='http://bb.com/blog/',
                                                      date=high_date)
        assert context['site_info'] == SiteInfo(site_name='HELLO',
                                                base_url='http://bb.com',
                                                section='blog')

    def test_date_sorting(self):
        section = Section('blog')
        section.append_content_file(self.make_content_file('blog', 'top-content', 'The Entry'))
        section.append_content_file(self.make_content_file('blog', 'middle-content', 'The Entry',
                                                           date=datetime.now() - timedelta(hours=1)))
        section.append_content_file(self.make_content_file('blog', 'bottom-content', 'The Entry',
                                                           date=datetime.now() - timedelta(hours=2)))
        context = section.get_context(CONFIG)
        items = context['items']
        assert len(items) == 3
        assert items[0].name == 'top-content.md'
        assert items[1].name == 'middle-content.md'
        assert items[2].name == 'bottom-content.md'

    def test_render(self):
        section = Section('blog')
        section.append_content_file(self.make_content_file('blog', 'the-content', 'The Entry', draft=True))
        templates = FakeTemplates([FakeTemplate('list.html')])
        rendered = section.render(CONFIG, templates, self.workdir.name)
        assert os.path.exists(os.path.join(self.workdir.name, 'blog/index.html'))
