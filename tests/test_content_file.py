import os
import unittest
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

from markupsafe import Markup
from markdown import markdown

from sitegen.content import ContentFile, Section
from common import FakeTemplate, FakeTemplates

MD_CONTENT = """title: Blog Post One
date: 28.02.2021 15:30
draft: false
tags: programming, software development, bash-works?

This is the content of the post.
"""

class ContentFileTests(unittest.TestCase):

    def setUp(self):
        self.workdir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.workdir.cleanup()

    def test_slug(self):
        cf = ContentFile('', 'the-entry.md', '/tmp/the-entry.md')
        assert cf.slug == 'the-entry'

    def test_get_output_directory_no_section(self):
        cf = ContentFile('', 'the-entry.md', '/tmp/the-entry.md')
        assert cf.get_output_directory('/tmp/public') == '/tmp/public/the-entry'


    def test_get_output_directory_index(self):
        cf = ContentFile('', 'index.md', '/tmp/the-entry.md')
        assert cf.get_output_directory('/tmp/public') == '/tmp/public'


    def test_get_output_directory_section_index(self):
        cf = ContentFile('blog', 'index.md', '/tmp/index.md')
        assert cf.get_output_directory('/tmp/public') == '/tmp/public/blog/index'


    def test_get_template_index(self):
        cf = ContentFile('', 'index.md', '/tmp/index.md')
        templates = FakeTemplates([FakeTemplate('index.html')])
        template = cf.get_template(templates)
        assert template.path == 'index.html'

    def test_get_template_single(self):
        cf = ContentFile('', 'the-entry.md', '/tmp/the-entry.md')
        templates = FakeTemplates([FakeTemplate('single.html')])
        template = cf.get_template(templates)
        assert template.path == 'single.html'

    def test_get_template_section_single(self):
        # The section single should be preferred
        cf = ContentFile('blog', 'the-entry.md', '/tmp/the-entry.md')
        templates = FakeTemplates([FakeTemplate('single.html'), FakeTemplate('blog/single.html')])
        template = cf.get_template(templates)
        assert template.path == 'blog/single.html'

    def test_get_template_section_no_single(self):
        # If single for section does not exist, use default
        cf = ContentFile('blog', 'the-entry.md', '/tmp/the-entry.md')
        templates = FakeTemplates([FakeTemplate('single.html')])
        template = cf.get_template(templates)
        assert template.path == 'single.html'

    def make_content_file(self, contentfile_name, contents):
        path = Path(self.workdir.name) / contentfile_name
        path.write_text(contents)
        return path

    def test_context(self):
        filepath = str(self.make_content_file('content.md', "The content is this"))
        cf = ContentFile('blog', 'content.md', filepath)
        existing_context = {'title': 'The Blog'}
        new_context = cf.get_context(existing_context)
        assert new_context is not existing_context
        assert new_context.pop('item') is cf
        assert ContentFile('', 'content.md', filepath).get_context({})['section'] == ''

    def test_web_path(self):
        cf = ContentFile('blog', 'the-entry.md', '/tmp/the-entry.md')
        assert cf.web_path == '/blog/the-entry'
        cf = ContentFile('', 'the-entry.md', '/tmp/the-entry.md')
        assert cf.web_path == '/the-entry'

    def test_load_properties(self):
        filepath = str(self.make_content_file('content.md', MD_CONTENT))
        cf = ContentFile('blog', 'the-entry.md', filepath)
        properties = cf.properties
        assert properties == {
            'title': 'Blog Post One',
            'draft': False,
            'date': datetime(2021, 2, 28, 15, 30),
            'tags': ['programming', 'software development', 'bash-works?']}

    def test_publish_date(self):
        filepath = str(self.make_content_file('content.md', MD_CONTENT))
        cf = ContentFile('blog', 'the-entry.md', filepath)
        assert cf.publish_date == datetime(2021, 2, 28, 15, 30)

    def test_publish_date_missing(self):
        content = "\n".join(line for line in MD_CONTENT.split("\n") if not line.startswith("date"))
        filepath = str(self.make_content_file('content.md', content))
        cf = ContentFile('blog', 'the-entry.md', filepath)
        assert datetime.now() - cf.publish_date < timedelta(milliseconds=1)


    def test_render(self):
        filepath = str(self.make_content_file('content.md', "The content is this"))
        cf = ContentFile('blog', 'the-entry.md', filepath)
        templates = FakeTemplates([FakeTemplate('blog/single.html')])
        public_dir = Path(self.workdir.name) /  'public'
        cf.render({'key': 'value'}, templates, str(public_dir))
        assert os.path.exists(os.path.join(public_dir, 'blog/the-entry/index.html'))


    def test_render_skip_draft(self):
        filepath = str(self.make_content_file('content.md', """draft: true

The content is this"""))
        cf = ContentFile('blog', 'the-entry.md', filepath)
        templates = FakeTemplates([FakeTemplate('blog/single.html')])
        public_dir = Path(self.workdir.name) /  'public'
        cf.render({'key': 'value'}, templates, str(public_dir))
        index_path = public_dir / "blog" / "the-entry" / "index.html"
        assert not index_path.exists()
