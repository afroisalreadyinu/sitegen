import os
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
        os.makedirs(public_dir, exist_ok=True)
        with open(os.path.join(public_dir, 'rss.xml'), 'w') as feed_file:
            feed_file.write(self.generate_feed(config))


    def generate_feed(self, config):
        items = []
        for cf in sorted(self.content_files, key=lambda x: x.publish_date, reverse=True):
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
