import unittest
import tempfile
import shutil
from pathlib import Path

from sitegen import content

class RenderTests(unittest.TestCase):

    def setUp(self):
        self.workdir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.workdir.cleanup()

    def test_render_index(self):
        base = Path(self.workdir.name)
        contents = base / "content"
        contents.mkdir()
        index = contents / "index.md"
        index.write_text("This is content")
        templates = base / "templates"
        templates.mkdir()
        index_template = templates / "index.html"
        index_template.write_text("""<html><body>{{ item.html_content }}</body></html>""")

        content.generate_site(str(base), {'title': 'Test'})

        public = base / "public"
        assert public.is_dir()
        index = public / "index.html"
        assert index.exists()
        index_contents = index.read_text()
        assert index_contents == "<html><body><p>This is content</p></body></html>"
