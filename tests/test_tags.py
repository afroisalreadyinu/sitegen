import unittest
import tempfile
from pathlib import Path
from datetime import datetime, timedelta

from sitegen.content import TagCollection

from common import FakeTemplate, FakeTemplates, CollectionTestBase

class TagCollectionTests(unittest.TestCase, CollectionTestBase):

    def setUp(self):
        self.workdir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.workdir.cleanup()

    def test_get_context(self):
        tc = TagCollection('test')
        tc.append_content_file(self.make_content_file('blog', 'the-entry', 'The Entry'))
        context = tc.get_context({'title': 'The Tag', 'baseurl': 'http://bb.com'})
        assert 'items' in context
        assert len(context.pop('items')) == 1
        assert context == {'tag': 'test',
                           'baseurl': 'http://bb.com',
                           'title': 'The Tag',
                           'pageurl': 'http://bb.com/tag/test'}


    def test_date_sorting(self):
        tc = TagCollection('blog')
        tc.append_content_file(self.make_content_file('blog', 'top-content', 'The Entry'))
        tc.append_content_file(self.make_content_file('blog', 'middle-content', 'The Entry',
                                                      date=datetime.now() - timedelta(hours=1)))
        tc.append_content_file(self.make_content_file('blog', 'bottom-content', 'The Entry',
                                                      date=datetime.now() - timedelta(hours=2)))
        context = tc.get_context({'baseurl': 'http://bb.com'})
        items = context['items']
        assert len(items) == 3
        assert items[0].name == 'top-content'
        assert items[1].name == 'middle-content'
        assert items[2].name == 'bottom-content'

    def test_skip_draft(self):
        tc = TagCollection('blog')
        tc.append_content_file(self.make_content_file('blog', 'the-content', 'The Entry', draft=True))
        tc.append_content_file(self.make_content_file('blog', 'other-content', 'The Entry', draft=False))
        context = tc.get_context({'baseurl': 'http://bb.com'})
        assert len(context['items']) == 1
        assert context['items'][0].name == 'other-content'

    def test_render(self):
        tc = TagCollection('tech')
        tc.append_content_file(self.make_content_file('blog', 'the-content', 'The Entry', draft=True))
        templates = FakeTemplates([FakeTemplate('list.html')])
        with tempfile.TemporaryDirectory() as tmpdirname:
            rendered = tc.render({'title': 'The Blog', 'baseurl': 'http://bb.com'}, templates, tmpdirname)
            output_path = Path(tmpdirname) / 'tag/tech/index.html'
            assert output_path.exists()
            assert output_path.read_text().startswith('list.html')

    def test_prefer_tag_template(self):
        tc = TagCollection('tech')
        tc.append_content_file(self.make_content_file('blog', 'the-content', 'The Entry', draft=True))
        templates = FakeTemplates([FakeTemplate('list.html'), FakeTemplate('tag.html')])
        with tempfile.TemporaryDirectory() as tmpdirname:
            tc.render({'title': 'The Blog', 'baseurl': 'http://bb.com'}, templates, tmpdirname)
            output_path = Path(tmpdirname) / 'tag/tech/index.html'
            assert output_path.exists()
            assert output_path.read_text().startswith('tag.html')
