import os
import unittest
from unittest import mock
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

from markupsafe import Markup
from markdown import markdown

from sitegen.content import ContentFile, Section, PageContent, SiteInfo
from common import FakeTemplate, FakeTemplates

MD_CONTENT = """title: Blog Post One
date: 09.02.2021 15:30
draft: false
tags: programming, software development, bash-works?

This is the content of the post.
"""

CONFIG = {'site': {'url': 'http://bb.com', 'title': 'HELLO'}}

class ContentFileTests(unittest.TestCase):

    def setUp(self):
        self.workdir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.workdir.cleanup()

    def test_slug(self):
        cf = ContentFile('', 'the-entry.md', '/tmp/the-entry.md')
        assert cf.slug == 'the-entry'

    def test_get_output_directory_no_section(self):
        filepath = str(self.make_content_file('content.md', "The content is this"))
        cf = ContentFile('', 'the-entry.md', filepath)
        assert cf.get_output_directory('/tmp/public') == '/tmp/public/the-entry'


    def test_get_output_directory_index(self):
        filepath = str(self.make_content_file('content.md', "The content is this"))
        cf = ContentFile('', 'index.md', filepath)
        assert cf.get_output_directory('/tmp/public') == '/tmp/public'


    def test_get_output_directory_section_index(self):
        filepath = str(self.make_content_file('content.md', "The content is this"))
        cf = ContentFile('blog', 'index.md', filepath)
        assert cf.get_output_directory('/tmp/public') == '/tmp/public/blog/index'


    def test_get_output_directory_flat(self):
        filepath = str(self.make_content_file('content.md', """flat: true

The content is this"""))
        cf = ContentFile('blog', 'content.md', filepath)
        assert cf.get_output_directory('/tmp/public') == '/tmp/public/blog'


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

    def test_description(self):
        filepath = str(self.make_content_file('content.md', """description: The index page is full of content

The content is this"""))
        cf = ContentFile('blog', 'content.md', filepath)
        assert cf.description == "The index page is full of content"

    def test_description_no_description(self):
        filepath = str(self.make_content_file('content.md', "This is the content"))
        cf = ContentFile('blog', 'content.md', filepath)
        assert cf.description == ""


    @mock.patch('sitegen.content.datetime')
    def test_context_no_date(self, mock_datetime):
        mock_datetime.now.return_value = sentinel = object()
        filepath = str(self.make_content_file('content.md', "The content is this"))
        cf = ContentFile('blog', 'content.md', filepath)
        context = cf.get_context(CONFIG)
        assert context['page_content'] == PageContent(title='',
                                                      description='',
                                                      canonical_url='http://bb.com/blog/content',
                                                      date=sentinel)
        assert context['site_info'] == SiteInfo(site_name='HELLO', base_url='http://bb.com', section='blog')

    def test_context_empty_section(self):
        filepath = str(self.make_content_file('content.md', MD_CONTENT))
        cf = ContentFile('', 'content.md', filepath)
        context = cf.get_context(CONFIG)
        assert context['page_content'] == PageContent(title='Blog Post One',
                                                      description='',
                                                      canonical_url='http://bb.com/content',
                                                      date=datetime(2021, 2, 9, 15, 30))
        assert context['site_info'] == SiteInfo(site_name='HELLO', base_url='http://bb.com', section='')


    def test_context_index_page(self):
        filepath = str(self.make_content_file('index.md', MD_CONTENT))
        cf = ContentFile('', 'index.md', filepath)
        context = cf.get_context(CONFIG)
        assert context['page_content'] == PageContent(title='Blog Post One',
                                                      description='',
                                                      canonical_url='http://bb.com/',
                                                      date=datetime(2021, 2, 9, 15, 30))
        assert context['site_info'] == SiteInfo(site_name='HELLO', base_url='http://bb.com', section='')

    def test_context_item(self):
        filepath = str(self.make_content_file('index.md', MD_CONTENT))
        cf = ContentFile('', 'index.md', filepath)
        context = cf.get_context(CONFIG)
        assert context['item'] is cf

    def test_web_path(self):
        cf = ContentFile('blog', 'the-entry.md', '/tmp/the-entry.md')
        assert cf.web_path == '/blog/the-entry'
        cf = ContentFile('', 'the-entry.md', '/tmp/the-entry.md')
        assert cf.web_path == '/the-entry'
        cf = ContentFile('', 'index.md', '/tmp/the-entry.md')
        assert cf.web_path == '/'

    def test_load_properties(self):
        filepath = str(self.make_content_file('content.md', MD_CONTENT))
        cf = ContentFile('blog', 'the-entry.md', filepath)
        properties = cf.properties
        assert properties == {
            'title': 'Blog Post One',
            'draft': False,
            'date': datetime(2021, 2, 9, 15, 30),
            'tags': 'programming, software development, bash-works?'}

    def test_publish_date(self):
        filepath = str(self.make_content_file('content.md', MD_CONTENT))
        cf = ContentFile('blog', 'the-entry.md', filepath)
        assert cf.publish_date == datetime(2021, 2, 9, 15, 30)

    def test_publish_date_missing(self):
        content = "\n".join(line for line in MD_CONTENT.split("\n") if not line.startswith("date"))
        filepath = str(self.make_content_file('content.md', content))
        cf = ContentFile('blog', 'the-entry.md', filepath)
        assert datetime.now() - cf.publish_date < timedelta(milliseconds=1)

    def test_tags_empty(self):
        content = '\n'.join([x for x in MD_CONTENT.split('\n') if not x.startswith('tags:')])
        filepath = str(self.make_content_file('content.md', content))
        cf = ContentFile('blog', 'the-entry.md', filepath)
        assert cf.tags == []

    def test_tags(self):
        filepath = str(self.make_content_file('content.md', MD_CONTENT))
        cf = ContentFile('blog', 'the-entry.md', filepath)
        assert cf.tags == ['programming', 'software development', 'bash-works?']

    def test_render(self):
        filepath = str(self.make_content_file('content.md', "The content is this"))
        cf = ContentFile('blog', 'the-entry.md', filepath)
        templates = FakeTemplates([FakeTemplate('blog/single.html')])
        public_dir = Path(self.workdir.name) /  'public'
        cf.render(CONFIG, templates, str(public_dir))
        assert os.path.exists(os.path.join(public_dir, 'blog/the-entry/index.html'))


    def test_render_skip_draft(self):
        filepath = str(self.make_content_file('content.md', """draft: true

The content is this"""))
        cf = ContentFile('blog', 'the-entry.md', filepath)
        templates = FakeTemplates([FakeTemplate('blog/single.html')])
        public_dir = Path(self.workdir.name) /  'public'
        cf.render(CONFIG, templates, str(public_dir))
        index_path = public_dir / "blog" / "the-entry" / "index.html"
        assert not index_path.exists()

    def test_render_flat_content_file(self):
        """If the `flat` property is set in the content file, do not render to a
        directory with index.html, but instead into a same-named html file"""
        filepath = str(self.make_content_file('content.md', """flat: true

The content is this"""))
        cf = ContentFile('blog', 'the-entry.md', filepath)
        templates = FakeTemplates([FakeTemplate('blog/single.html')])
        public_dir = Path(self.workdir.name) /  'public'
        cf.render(CONFIG, templates, str(public_dir))
        index_path = public_dir / "blog" / "the-entry" / "index.html"
        assert not index_path.exists()
        file_path = public_dir / "blog" / "the-entry.html"
