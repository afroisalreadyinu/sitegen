from pathlib import Path
import tempfile

from jinja2.exceptions import TemplateNotFound

from sitegen.content import ContentFile

class FakeTemplate:
    def __init__(self, path):
        self.path = path
        self.render_context = None

    def render(self, **context):
        self.render_context = context
        return '{}: {}'.format(self.path, ''.join(str(x) for x in context.values()))

class FakeTemplates:
    def __init__(self, templates):
        self.templates = templates

    def get_template(self, template_path):
        for template in self.templates:
            if template.path == template_path:
                return template
        raise TemplateNotFound(template_path)


class CollectionTestBase:

    def make_content_file(self, section, name, title, draft=False, date=None):
        content_file = Path(self.workdir.name) / f"{name}.md"
        is_draft = str(draft).lower()
        date = f'date: {date.strftime("%d.%m.%Y %H:%M")}\n' if date else ''
        content_file.write_text(f"""title: {title}
draft: {is_draft}
{date}
The content
""")
        return ContentFile(section, name, str(content_file))
