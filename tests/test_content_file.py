import os
import unittest
import tempfile
from datetime import datetime

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
        Section.AllSections = {}

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

    def test_context(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            filepath = os.path.join(tmpdirname, 'content.md')
            with open(filepath, 'w') as content_file:
                content_file.write("The content is this")
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
        with tempfile.TemporaryDirectory() as tmpdirname:
            filepath = os.path.join(tmpdirname, 'content.md')
            with open(filepath, 'w') as content_file:
                content_file.write(MD_CONTENT)
            cf = ContentFile('blog', 'the-entry.md', filepath)
            properties = cf.properties
        assert properties == {
            'title': 'Blog Post One',
            'draft': False,
            'date': datetime(2021, 2, 28, 15, 30),
            'tags': ['programming', 'software development', 'bash-works?']}


    def test_render(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            filepath = os.path.join(tmpdirname, 'content.md')
            with open(filepath, 'w') as content_file:
                content_file.write("The content is this")
            cf = ContentFile('blog', 'the-entry.md', filepath)
            templates = FakeTemplates([FakeTemplate('blog/single.html')])
            public_dir = os.path.join(tmpdirname, 'public')
            cf.render({'key': 'value'}, templates, public_dir)
            assert os.path.exists(os.path.join(public_dir, 'blog/the-entry/index.html'))


    def test_render_skip_draft(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            filepath = os.path.join(tmpdirname, 'content.md')
            with open(filepath, 'w') as content_file:
                content_file.write("""draft: true

The content is this""")
            cf = ContentFile('blog', 'the-entry.md', filepath)
            templates = FakeTemplates([FakeTemplate('blog/single.html')])
            public_dir = os.path.join(tmpdirname, 'public')
            cf.render({'key': 'value'}, templates, public_dir)
            assert not os.path.exists(os.path.join(public_dir, 'blog/the-entry/index.html'))
