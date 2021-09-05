import datetime

import rfeed
from furl import furl

def generate_feed(config, content_files): # list[ContentFile]
    items = []
    for cf in content_files:
        url = furl(config['site']['url']) / cf.web_path
        item = rfeed.Item(title=cf.properties['title'],
	                  link=url,
	                  description=cf.description,
                          author=config['site']['author'],
                          guid=rfeed.Guid(url),
	                  pubDate=cf.publish_date)
    feed = rfeed.Feed(title=f"{config['site']['title']} RSS Feed",
	              link="http://www.example.com/rss",
	              description="This is an example of how to use rfeed to generate an RSS 2.0 feed",
	              language="en-US",
	              lastBuildDate=datetime.datetime.now(),
	              items=items)
    return feed.rss()
