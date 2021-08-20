import unittest
import tempfile

from sitegen.content import TagCollection

from common import FakeTemplate, FakeTemplates, CollectionTestBase

class TagCollectionTests(unittest.TestCase, CollectionTestBase):

    def setUp(self):
        self.workdir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.workdir.cleanup()

    def test_get_context(self):
        tc = TagCollection('test')
        tc.append_content_file(self.make_content_file('blog', 'the-entry', 'The Entry'))
        context = tc.get_context({})
        assert 'items' in context
        assert len(context.pop('items')) == 1
        assert context == {'tag': 'test'}
