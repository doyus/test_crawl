#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
'''
@Project ：crawl 
@File    ：run_task.py
@IDE     ：PyCharm 
@INFO     ： 
@Author  ：BGSPIDER
@Date    ：14/11/2024 下午2:09 
'''
import re

from scrapyd_api.API import ScrapydAPI
scrapyd = ScrapydAPI('http://localhost:6800')
from loguru import logger as  logging
from utils.db import *
import time
def check_run(id):
    while True:
        ststus = scrapyd.job_status('crawl', id)
        if ststus=='finished':
            logging.error('程序结束')
            # 预留日志接口
            log=scrapyd.log('./logs','crawl','crawl_html',id)
            print(log)
            site_id=re.findall('任务id是:(.*?);;',log)[0]
            update_scrapy_log(site_id=site_id,log=log)
            # print(log)
            return True
        else:
            time.sleep(3)
            continue
for x in range(1):
    job_id=scrapyd.schedule('crawl', 'crawl_html',v9_id=2145645)
    logging.error(f'程序启动：{job_id}')
    if check_run(job_id):
        continue
    else:
        logging.error('1111111111111111111111111111')
        break
