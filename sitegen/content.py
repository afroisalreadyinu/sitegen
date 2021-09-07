import os
import copy
import glob
from dataclasses import dataclass, field
from typing import Dict
from datetime import datetime
from dataclasses import dataclass

from furl import furl
from jinja2 import Environment, FileSystemLoader, select_autoescape, Markup
from jinja2.exceptions import TemplateNotFound

from markupsafe import Markup
from markdown import Markdown

@dataclass
class PageContent:
    title: str
    description: str
    canonical_url: str
    date: datetime

@dataclass
class SiteInfo:
    site_name: str
    base_url: str
    section: str


class RenderMixin:

    def get_filename(self):
        return "index.html"

    def render(self, config: Dict, templates, public_dir: str):
        context = self.get_context(config)
        template = self.get_template(templates)
        directory = self.get_output_directory(public_dir)
        os.makedirs(directory, exist_ok=True)
        filepath = os.path.join(directory, self.get_filename())
        with open(filepath, "w") as target_file:
            target_file.write(template.render(**context))

def dateparse(datestr):
    return datetime.strptime(datestr, "%d.%m.%Y %H:%M")

def sort_by_date(content_files):
    return sorted((x for x in content_files if not x.is_draft),
                  key=lambda x: x.publish_date,
                  reverse=True)

class Section(RenderMixin):

    def __init__(self, name):
        assert name
        self.name = name
        self.content_files = []

    def append_content_file(self, content_file):
        assert self.name == content_file.section
        self.content_files.append(content_file)

    def get_context(self, config):
        context = {}
        context['items'] = sort_by_date(self.content_files)
        url = furl(config['site']['url']).set(path=f"/{self.name}/").url
        context['page_content'] = PageContent(title=self.name,
                                              description='',
                                              canonical_url=url,
                                              date=max(x.publish_date for x in self.content_files))
        context['site_info'] = SiteInfo(site_name=config['site']['title'],
                                        base_url=config['site']['url'],
                                        section=self.name)
        return context

    def get_template(self, templates):
        try:
            template = templates.get_template(f"{self.name}/list.html")
        except TemplateNotFound:
            template = templates.get_template("list.html")
        return template

    def get_output_directory(self, public_dir):
        # public/$section/index.html
        return os.path.join(public_dir, self.name)


class TagCollection(RenderMixin):

    def __init__(self):
        self.content_tags = {}

    def append_content_file(self, content_file):
        for tag in content_file.tags:
            ct = self.content_tags.get(tag)
            if not ct:
                ct = ContentTag(tag)
                self.content_tags[tag] = ct
            ct.append_content_file(content_file)

    @property
    def items(self):
        return sorted(self.content_tags.values(), key=lambda x: x.tag)

    def get_context(self, site_config):
        context = {}
        context['items'] = self.items
        url = furl(site_config['site']['url']).set(path="/tag/").url
        context['page_content'] = PageContent(title='Tags',
                                              description='',
                                              canonical_url=url,
                                              date=max(x.publish_date for x in self.items))
        context['site_info'] = SiteInfo(site_name=site_config['site']['title'],
                                        base_url=site_config['site']['url'],
                                        section='tag')
        return context

    def get_template(self, templates):
        try:
            template = templates.get_template("tags.html")
        except TemplateNotFound:
            template = templates.get_template("list.html")
        return template

    def get_output_directory(self, public_dir):
        # public/tag/
        return os.path.join(public_dir, "tag")

    def render(self, config, templates, public_dir):
        if not self.content_tags:
            return
        for ct in self.content_tags.values():
            ct.render(config, templates, public_dir)
        super().render(config, templates, public_dir)


class ContentTag(RenderMixin):

    def __init__(self, tag):
        assert tag
        self.tag = tag
        self.content_files = []

    def append_content_file(self, content_file):
        self.content_files.append(content_file)

    @property
    def web_path(self):
        return f"/tag/{self.tag}"

    @property
    def publish_date(self):
        items = sort_by_date(self.content_files)
        if not items:
            # This can only happen if the content is only draft, in that case
            # pick the youngest draft
            date = max(x.publish_date for x in self.content_files)
        else:
            date = max(x.publish_date for x in items)
        return date

    def get_context(self, config):
        context = {}
        context['items'] = sort_by_date(self.content_files)
        context['tag'] = self.tag
        url = furl(config['site']['url']).set(path=self.web_path).url
        context['page_content'] = PageContent(title=self.tag,
                                              description='',
                                              canonical_url=url,
                                              date=self.publish_date)
        context['site_info'] = SiteInfo(site_name=config['site']['title'],
                                        base_url=config['site']['url'],
                                        section='tag')
        return context
        return context

    def get_template(self, templates):
        try:
            template = templates.get_template("tag.html")
        except TemplateNotFound:
            template = templates.get_template("list.html")
        return template

    def get_output_directory(self, public_dir):
        # public/tags/$tag/index.html
        return os.path.join(public_dir, "tag", self.tag)


class ContentContext:

    def __init__(self):
        self.content_files = []
        self.sections = {}
        self.tag_collection = TagCollection()
        self.feed_generator = FeedGenerator()

    def add_content_file(self, content_file):
        self.content_files.append(content_file)
        self.add_to_section(content_file)
        self.tag_collection.append_content_file(content_file)
        self.feed_generator.append_content_file(content_file)

    def add_to_section(self, content_file):
        section_name = content_file.section
        if not section_name:
            return
        section = self.sections.get(section_name)
        if not section:
            section = Section(section_name)
            self.sections[section_name] = section
        section.append_content_file(content_file)

    def render_contents(self, config, templates, public_dir):
        for content in self.content_files:
            content.render(config, templates, public_dir)

    def render_sections(self, config, templates, public_dir):
        for section in self.sections.values():
            section.render(config, templates, public_dir)

    def render(self, config, templates, public_dir):
        self.render_contents(config, templates, public_dir)
        self.render_sections(config, templates, public_dir)
        self.tag_collection.render(config, templates, public_dir)
        self.feed_generator.render(config, public_dir)

    @classmethod
    def load_directory(cls, basedir: str):
        content_context = cls()
        contentdir = os.path.join(basedir, "content")
        for root, dirs, files in os.walk(contentdir):
            for filename in files:
                if not filename.endswith('.md'):
                    continue
                if filename.startswith('.'):
                    # dotfiles are used for all kinds of weird purposes,
                    # including as backup by e.g. Emacs
                    continue
                path = os.path.join(root, filename)
                filename = path[len(contentdir):].lstrip('/')
                if '/' in filename:
                    section, name = filename.split('/', 1)
                else:
                    section = ''
                    name = filename
                content_file = ContentFile(section=section, name=name, abspath=path)
                content_context.add_content_file(content_file)
        return content_context


class ContentFile(RenderMixin):

    def __init__(self, section: str, name: str, abspath: str):
        self.section = section
        self.name = name
        self.abspath = abspath
        self._html_content = None
        self._metadata = None
        self._markdown = None

    @property
    def html_content(self):
        if self._html_content is not None:
            return self._html_content
        with open(self.abspath, 'r') as md_content_file:
            md_content = md_content_file.read()
        self._markdown = Markdown(extensions=['smarty', 'meta', 'fenced_code', 'codehilite'])
        self._html_content = Markup(self._markdown.convert(md_content))
        return self._html_content

    @property
    def properties(self):
        if self._metadata is not None:
            return self._metadata
        _ = self.html_content
        self._metadata = {key: (value[0] if isinstance(value, list) else value)
                          for (key, value) in self._markdown.Meta.items()}
        if 'title' not in self._metadata:
            self._metadata['title'] = ''
        if 'date' in self._metadata:
            self._metadata['date'] = dateparse(self._metadata['date'])
        if 'draft' in self._metadata:
            value = self._metadata['draft']
            assert value in ['true', 'false']
            self._metadata['draft'] = value == 'true'
        return self._metadata

    @property
    def publish_date(self):
        return self.properties.get('date', datetime.now())

    @property
    def slug(self):
        return self.name[:-len(".md")]

    @property
    def web_path(self):
        if self.name == 'index.md':
            return "/"
        if not self.section:
            return f"/{self.slug}"
        return f"/{self.section}/{self.slug}"

    @property
    def is_draft(self):
        return self.properties.get('draft', False)

    @property
    def tags(self):
        return [x.strip() for x in self.properties.get('tags', '').split(',') if x.strip()]

    @property
    def description(self):
        return self.properties.get('description', '')

    def get_context(self, site_config):
        context = {}
        context['page_content'] = PageContent(
            title=self.properties['title'],
            description=self.description,
            canonical_url=furl(site_config['site']['url']).set(path=self.web_path).url,
            date=self.publish_date)
        context['site_info'] = SiteInfo(site_name=site_config['site']['title'],
                                        base_url=site_config['site']['url'],
                                        section=self.section)
        context['item'] = self
        return context

    def get_template(self, templates):
        if not self.section:
            if self.name == 'index.md':
                template = templates.get_template("index.html")
            else:
                template = templates.get_template("single.html")
        else:
            try:
                template = templates.get_template(f"{self.section}/single.html")
            except TemplateNotFound:
                template = templates.get_template("single.html")
        return template

    def get_filename(self):
        flat = self.properties.get('flat', False)
        if flat:
            return self.name[:-len(".md")] + ".html"
        else:
            return "index.html"

    def get_output_directory(self, public_dir):
        flat = self.properties.get('flat', False)
        if not self.section:
            if self.name == 'index.md':
                return public_dir
            # public/$filename/index.html
            if flat:
                return public_dir
            else:
                return os.path.join(public_dir, self.slug)
        if flat:
            # public/$section/
            return os.path.join(public_dir, self.section)
        else:
            # public/$section/$filename/
            return os.path.join(public_dir, self.section, self.name[:-len(".md")])

    def render(self, *args, **kwargs):
        if self.is_draft:
            return
        super().render(*args, **kwargs)


def to_date(dt):
    """Format a datetime as only date"""
    return dt.strftime('%d.%m.%Y')

def generate_site(basedir, config):
    content_context = ContentContext.load_directory(basedir)
    env = Environment(
        loader=FileSystemLoader(os.path.join(basedir, "templates")),
        autoescape=True
    )
    env.filters['to_date'] = to_date
    target = os.path.join(basedir, 'public')
    os.makedirs(target, exist_ok=True)
    content_context.render(config, env, target)
