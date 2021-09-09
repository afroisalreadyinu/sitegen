import unittest
from unittest import mock

import pytest

from sitegen import main

class ConfigSchemaTests(unittest.TestCase):

    @mock.patch('sitegen.main.toml')
    def test_load_config(self, mock_toml):
        mock_toml.load.return_value = {'site': {'url': 'http://bb.com',
                                                'title': 'HELLO',
                                                'author': 'Sid Vicious',
                                                'locale': 'en-US'}}
        config = main.load_config()


    @mock.patch('sitegen.main.toml')
    def test_load_config_missing_field(self, mock_toml):
        mock_toml.load.return_value = {'site': {'url': 'http://bb.com',
                                                'author': 'Sid Vicious',
                                                'locale': 'en-US'}}
        with pytest.raises(main.SitegenConfigurationError) as context:
            config = main.load_config()
        assert "Missing key: 'title'" in context.value.args[0]

    @mock.patch('sitegen.main.toml')
    def test_load_config_invalid_url(self, mock_toml):
        mock_toml.load.return_value = {'site': {'url': 'ttp://bb.com',
                                                'title': 'HELLO',
                                                'author': 'Sid Vicious',
                                                'locale': 'en-US'}}
        with pytest.raises(main.SitegenConfigurationError) as context:
            config = main.load_config()
