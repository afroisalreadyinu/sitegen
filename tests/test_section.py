import os
import unittest
from types import SimpleNamespace as Bunch
import tempfile
from datetime import datetime, timedelta

from sitegen.content import Section
from common import FakeTemplate, FakeTemplates, CollectionTestBase

class SectionTests(unittest.TestCase, CollectionTestBase):

    def setUp(self):
        self.workdir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.workdir.cleanup()

    def test_get_context(self):
        section = Section('blog')
        section.append_content_file(self.make_content_file('blog', 'the-entry', 'The Entry'))
        section.append_content_file(self.make_content_file('blog', 'other-entry', 'Other Entry'))
        existing_context = {'title': 'The Blog', 'baseurl': 'http://bb.com'}
        new_context = section.get_context(existing_context)
        assert 'items' in new_context
        assert len(new_context.pop('items')) == 2
        assert new_context == {'section': 'blog',
                               'baseurl': 'http://bb.com',
                               'pageurl': 'http://bb.com/blog/',
                               'title': 'The Blog'}

    def test_date_sorting(self):
        section = Section('blog')
        section.append_content_file(self.make_content_file('blog', 'top-content', 'The Entry'))
        section.append_content_file(self.make_content_file('blog', 'middle-content', 'The Entry',
                                                           date=datetime.now() - timedelta(hours=1)))
        section.append_content_file(self.make_content_file('blog', 'bottom-content', 'The Entry',
                                                           date=datetime.now() - timedelta(hours=2)))
        existing_context = {'title': 'The Blog', 'baseurl': 'http://bb.com'}
        context = section.get_context(existing_context)
        items = context['items']
        assert len(items) == 3
        assert items[0].name == 'top-content'
        assert items[1].name == 'middle-content'
        assert items[2].name == 'bottom-content'

    def test_skip_draft(self):
        section = Section('blog')
        section.append_content_file(self.make_content_file('blog', 'the-content', 'The Entry', draft=True))
        section.append_content_file(self.make_content_file('blog', 'other-content', 'The Entry', draft=False))
        existing_context = {'title': 'The Blog', 'baseurl': 'http://bb.com'}
        context = section.get_context(existing_context)
        assert len(context['items']) == 1
        assert context['items'][0].name == 'other-content'

    def test_render(self):
        section = Section('blog')
        section.append_content_file(self.make_content_file('blog', 'the-content', 'The Entry', draft=True))
        templates = FakeTemplates([FakeTemplate('list.html')])
        with tempfile.TemporaryDirectory() as tmpdirname:
            rendered = section.render({'title': 'The Blog', 'baseurl': 'http://bb.com'},
                                      templates, tmpdirname)
            assert os.path.exists(os.path.join(tmpdirname, 'blog/index.html'))
