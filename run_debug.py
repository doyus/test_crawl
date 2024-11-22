#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
'''
@Project ：crawl 
@File    ：run_debug.py
@IDE     ：PyCharm 
@INFO     ： 
@Author  ：BGSPIDER
@Date    ：28/10/2024 下午3:42 
'''
from scrapy.cmdline import execute
execute('scrapy crawl crawl_html -a v9_id=2145645'.split())
# execute('scrapy crawl crawl_html -a id=27'.split())
# execute('scrapy crawl crawl_html -a id=196'.split())