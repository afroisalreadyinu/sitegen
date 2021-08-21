import unittest
import tempfile
from pathlib import Path

from sitegen.content import ContentFile, ContentContext
from common import FakeTemplates, FakeTemplate, CollectionTestBase

class ContentContextTests(unittest.TestCase, CollectionTestBase):

    def setUp(self):
        self.workdir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.workdir.cleanup()

    def test_add_content(self):
        context = ContentContext()
        content = self.make_content_file('blog', 'the-entry', 'The Entry')
        context.add_content_file(content)
        assert 'blog' in context.sections
        section = context.sections['blog']
        assert section.name == 'blog'
        assert len(section.content_files) == 1
        assert section.content_files[0] is content

    def test_add_content_existing_section(self):
        context = ContentContext()
        context.add_content_file(self.make_content_file('blog', 'the-entry', 'The Entry'))
        context.add_content_file(self.make_content_file('blog', 'other-entry', 'Other Entry'))
        assert 'blog' in context.sections
        section = context.sections['blog']
        assert len(section.content_files) == 2

    def test_skip_no_section(self):
        content = self.make_content_file('', 'the-entry', 'The Entry')
        context = ContentContext()
        context.add_content_file(content)
        assert len(context.sections) == 0

    def test_load_directory(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            basedir = Path(tmpdirname) / "content"
            basedir.mkdir()
            (basedir / 'index.md').write_text("Hello")
            (basedir / 'index.rst').write_text("Skip this")
            blog_dir = basedir / 'blog'
            blog_dir.mkdir()
            (blog_dir / 'blog-entry.md').write_text('Yolo')
            (blog_dir / '.#other-entry.md').write_text('Skip this')
            context = ContentContext.load_directory(tmpdirname)
        assert len(context.content_files) == 2
        assert sorted(x.name for x in context.content_files) == ['blog-entry.md', 'index.md']


    def test_render_sections(self):
        context = ContentContext()
        templates = FakeTemplates([FakeTemplate('list.html')])
        with tempfile.TemporaryDirectory() as tmpdirname:
            the_entry = Path(tmpdirname) / 'the-entry.md'
            the_entry.write_text("Hello")
            context.add_content_file(ContentFile('blog', 'the-entry', str(the_entry)))
            other_entry = Path(tmpdirname) / 'other-entry.md'
            other_entry.write_text("Hello")
            context.add_content_file(ContentFile('reviews', 'other-entry', str(other_entry)))
            context.render_sections({'title': 'Test'}, templates, tmpdirname)
