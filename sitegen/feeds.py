import datetime

import rfeed
from furl import furl

class FeedGenerator:

    def __init__(self):
        self.content_files = []

    def append_content_file(self, content_file):
        self.content_files.append(content_file)

    def render(self, config, public_dir):
        feed_content = self.generate_feed(config)

    def generate_feed(self, config):
        items = []
        for cf in self.content_files:
            url = furl(config['site']['url']) / cf.web_path
            item = rfeed.Item(title=cf.properties['title'],
                              link=url,
                              description=cf.description,
                              author=config['site']['author'],
                              guid=rfeed.Guid(url),
                              pubDate=cf.publish_date)
            items.append(item)
        feed = rfeed.Feed(title=f"{config['site']['title']} RSS Feed",
                          link="http://www.example.com/rss",
                          description="This is an example of how to use rfeed to generate an RSS 2.0 feed",
                          language="en-US",
                          lastBuildDate=datetime.datetime.now(),
                          items=items)
        return feed.rss()
