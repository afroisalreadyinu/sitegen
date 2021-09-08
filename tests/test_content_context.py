import unittest
import tempfile
from pathlib import Path

from sitegen.content import ContentFile, ContentContext
from common import FakeTemplates, FakeTemplate, CollectionTestBase

class ContentContextTests(unittest.TestCase, CollectionTestBase):
    """This class tests only the state of ContentContext. Render behavior is tested
    by test_render.py"""

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
        """Do not add a content file without section to any sections"""
        content = self.make_content_file('', 'the-entry', 'The Entry')
        context = ContentContext()
        context.add_content_file(content)
        assert len(context.sections) == 0

    def test_add_content_with_tag(self):
        context = ContentContext()
        context.add_content_file(self.make_content_file('', 'the-entry', 'The Entry', tags=['one', 'two']))
        context.add_content_file(self.make_content_file('', 'other-entry', 'Other Entry', tags=['two', 'three']))
        for tag in ['one', 'two', 'three']:
            assert tag in context.tag_collection.content_tags

    def test_load_directory(self):
        basedir = Path(self.workdir.name) / "content"
        basedir.mkdir()
        (basedir / 'index.md').write_text("Hello")
        (basedir / 'index.rst').write_text("Skip this")
        blog_dir = basedir / 'blog'
        blog_dir.mkdir()
        (blog_dir / 'blog-entry.md').write_text('Yolo')
        (blog_dir / '.#other-entry.md').write_text('Skip this')
        context = ContentContext.load_directory(self.workdir.name)
        assert len(context.content_files) == 2
        assert sorted(x.name for x in context.content_files) == ['blog-entry.md', 'index.md']

    def test_skip_draft(self):
        """If a content file is draft, just ignore it completely"""
        context = ContentContext()
        context.add_content_file(self.make_content_file('blog', 'the-entry',
                                                        'The Entry', tags=['one', 'two'], draft=True))
        assert context.content_files == []
        assert context.sections == {}
        assert context.tag_collection.content_tags == {}
