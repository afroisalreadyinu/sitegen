from jinja2.exceptions import TemplateNotFound

class FakeTemplate:
    def __init__(self, path):
        self.path = path
        self.render_context = None

    def render(self, **context):
        self.render_context = context
        return ''.join(str(x) for x in context.values())

class FakeTemplates:
    def __init__(self, templates):
        self.templates = templates

    def get_template(self, template_path):
        for template in self.templates:
            if template.path == template_path:
                return template
        raise TemplateNotFound(template_path)
