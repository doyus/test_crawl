# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from utils.mysql_db import *
from utils.db import *
from utils.tools import *
class CrawlPipeline:
    def process_item(self, item, spider):
        try:
            save_date = fromat_cms_data(dict(item))
            save_cms_api(save_date, item['site_id'])
            return item
        except Exception as e:
            print(e)
