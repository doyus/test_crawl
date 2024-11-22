# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class CrawlItem(scrapy.Item):
    TITLE=scrapy.Field()
    SITE_ID=scrapy.Field()
    SOURCE_URL=scrapy.Field()
    PUBLISH_DATE=scrapy.Field()
    CONTENT=scrapy.Field()
    classd_name=scrapy.Field()
    site_id=scrapy.Field()
    region=scrapy.Field()
    channel=scrapy.Field()
    DESCRIPTION=scrapy.Field()
    CATEGORY_ID=scrapy.Field()
