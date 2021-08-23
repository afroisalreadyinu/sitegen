import unittest
import tempfile
import shutil
from pathlib import Path

from sitegen import content

def make_dirs_and_files(basedir, structure):
    for key, value in structure.items():
        if isinstance(value, str):
            path = basedir / Path(key)
            path.write_text(value)
        else:
            newpath = basedir / Path(key)
            newpath.mkdir(exist_ok=True)
            make_dirs_and_files(newpath, value)


class RenderTests(unittest.TestCase):

    def setUp(self):
        self.workdir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.workdir.cleanup()

    def test_render_index(self):
        contents = {"content": {"index.md": "This is content"},
                    "templates": {"index.html": """<html><body>{{ item.html_content }}</body></html>"""}}
        base = Path(self.workdir.name)
        make_dirs_and_files(base, contents)

        content.generate_site(str(base), {'title': 'Test', 'baseurl': 'http://bb.com'})

        index = base / "public"/ "index.html"
        assert index.exists()
        assert index.read_text() == "<html><body><p>This is content</p></body></html>"


    def test_render_section_page(self):
        contents = {"content": {"index.md": "This is content",
                                "blog": {"post1.md": "This is post1"}},
                    "templates": {"index.html": """{{ item.html_content }}""",
                                  "single.html": """{{ item.html_content }}""",
                                  "list.html": """{% for item in items %}Link: {{ item.web_path }}{% endfor %}"""}}
        base = Path(self.workdir.name)
        make_dirs_and_files(base, contents)

        content.generate_site(str(base), {'title': 'Test', 'baseurl': 'http://bb.com'})

        section_index = base / "public" / "blog" / "index.html"
        assert section_index.exists()
        assert section_index.read_text() == "Link: /blog/post1"

        post_page = base / "public" / "blog" / "post1" / "index.html"
        assert post_page.exists()
        assert post_page.read_text() == "<p>This is post1</p>"


    def test_render_tags_pages(self):
        contents = {"content": {"index.md": "This is content",
                                "blog": {"post1.md": """tags: tech, sw development

This is post1
"""}},
                    "templates": {"index.html": """{{ item.html_content }}""",
                                  "single.html": """{{ item.html_content }}""",
                                  "list.html": """{% for item in items %}Link: {{ item.web_path }} {% endfor %}""",
                                  "tag.html": """Tag: {{ tag }} {% for item in items %}Link: {{ item.web_path }}{% endfor %}
"""}}
        base = Path(self.workdir.name)
        make_dirs_and_files(base, contents)

        content.generate_site(str(base), {'title': 'Test', 'baseurl': 'http://bb.com'})

        tag_index = base / "public" / "tag" /  "index.html"
        assert tag_index.exists()
        assert tag_index.read_text() == "Link: /tag/sw development Link: /tag/tech "

        tech_index = base / "public" / "tag" / "tech" / "index.html"
        assert tech_index.exists()
        assert tech_index.read_text() == "Tag: tech Link: /blog/post1"
