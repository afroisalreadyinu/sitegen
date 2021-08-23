import unittest
import tempfile
from pathlib import Path
from datetime import datetime, timedelta

from sitegen.content import ContentTag, TagCollection

from common import FakeTemplate, FakeTemplates, CollectionTestBase

class ContentTagTests(unittest.TestCase, CollectionTestBase):

    def setUp(self):
        self.workdir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.workdir.cleanup()

    def test_get_context(self):
        ct = ContentTag('test')
        ct.append_content_file(self.make_content_file('blog', 'the-entry', 'The Entry'))
        context = ct.get_context({'title': 'The Tag', 'baseurl': 'http://bb.com'})
        assert 'items' in context
        assert len(context.pop('items')) == 1
        assert context == {'tag': 'test',
                           'baseurl': 'http://bb.com',
                           'title': 'The Tag',
                           'pageurl': 'http://bb.com/tag/test'}


    def test_date_sorting(self):
        ct = ContentTag('blog')
        ct.append_content_file(self.make_content_file('blog', 'top-content', 'The Entry'))
        ct.append_content_file(self.make_content_file('blog', 'middle-content', 'The Entry',
                                                      date=datetime.now() - timedelta(hours=1)))
        ct.append_content_file(self.make_content_file('blog', 'bottom-content', 'The Entry',
                                                      date=datetime.now() - timedelta(hours=2)))
        context = ct.get_context({'baseurl': 'http://bb.com'})
        items = context['items']
        assert len(items) == 3
        assert items[0].name == 'top-content'
        assert items[1].name == 'middle-content'
        assert items[2].name == 'bottom-content'

    def test_skip_draft(self):
        ct = ContentTag('blog')
        ct.append_content_file(self.make_content_file('blog', 'the-content', 'The Entry', draft=True))
        ct.append_content_file(self.make_content_file('blog', 'other-content', 'The Entry', draft=False))
        context = ct.get_context({'baseurl': 'http://bb.com'})
        assert len(context['items']) == 1
        assert context['items'][0].name == 'other-content'

    def test_render(self):
        ct = ContentTag('tech')
        ct.append_content_file(self.make_content_file('blog', 'the-content', 'The Entry', draft=True))
        templates = FakeTemplates([FakeTemplate('list.html')])
        with tempfile.TemporaryDirectory() as tmpdirname:
            rendered = ct.render({'title': 'The Blog', 'baseurl': 'http://bb.com'}, templates, tmpdirname)
            output_path = Path(tmpdirname) / 'tag/tech/index.html'
            assert output_path.exists()
            assert output_path.read_text().startswith('list.html')

    def test_prefer_tag_template(self):
        ct = ContentTag('tech')
        ct.append_content_file(self.make_content_file('blog', 'the-content', 'The Entry', draft=True))
        templates = FakeTemplates([FakeTemplate('list.html'), FakeTemplate('tag.html')])
        with tempfile.TemporaryDirectory() as tmpdirname:
            ct.render({'title': 'The Blog', 'baseurl': 'http://bb.com'}, templates, tmpdirname)
            output_path = Path(tmpdirname) / 'tag/tech/index.html'
            assert output_path.exists()
            assert output_path.read_text().startswith('tag.html')

class TagCollectionTests(unittest.TestCase, CollectionTestBase):

    def setUp(self):
        self.workdir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.workdir.cleanup()

    def test_append_content_file(self):
        tc = TagCollection()
        cf = self.make_content_file('blog', 'the-entry', 'The Entry', tags=['hello', 'why-not'])
        tc.append_content_file(cf)
        assert len(tc.content_tags) == 2
        for tag in ['hello', 'why-not']:
            content_tag = tc.content_tags[tag]
            assert content_tag.content_files[0] is cf

    def test_get_context(self):
        tc = TagCollection()
        cf = self.make_content_file('blog', 'the-entry', 'The Entry', tags=['hello', 'why-not'])
        tc.append_content_file(cf)
        existing_context = {'title': 'The Blog', 'baseurl': 'http://bb.com'}
        new_context = tc.get_context(existing_context)
        assert new_context.pop('items') == list(tc.content_tags.values())
        assert new_context == {'title': 'The Blog',
                               'baseurl': 'http://bb.com',
                               'pageurl': 'http://bb.com/tag/'}

    def test_render_empty(self):
        """If there are no tags, don't do anything"""
        tc = TagCollection()
        templates = FakeTemplates([FakeTemplate('list.html')])
        tc.render({'title': 'The Blog', 'baseurl': 'http://bb.com'}, templates, self.workdir.name)
        tag_index = Path(self.workdir.name) / 'tag' / 'index.html'
        assert not tag_index.exists()


    def test_render(self):
        tc = TagCollection()
        cf = self.make_content_file('blog', 'the-entry', 'The Entry', tags=['hello', 'why-not'])
        tc.append_content_file(cf)
        templates = FakeTemplates([FakeTemplate('list.html')])
        tc.render({'title': 'The Blog', 'baseurl': 'http://bb.com'}, templates, self.workdir.name)
        tag_index = Path(self.workdir.name) / 'tag' / 'index.html'
        assert tag_index.exists()
        hello_index = Path(self.workdir.name) / 'tag' / 'hello' / 'index.html'
        assert hello_index.exists()
        whynot_index = Path(self.workdir.name) / 'tag' / 'why-not' / 'index.html'
        assert whynot_index.exists()
