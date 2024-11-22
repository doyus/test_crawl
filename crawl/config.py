#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
'''
@Project ：gxcx_crawl 
@File    ：config.py
@IDE     ：PyCharm 
@INFO     ： 
@Author  ：BGSPIDER
@Date    ：14/12/2023 下午2:43 
'''

REDIS_KEY_NAME_PREFIX = 'rules'
REDIS_HOST = 'r-.redis.rds.aliyuncs.com'
REDIS_PORT = '6379'
REDIS_DB = 1
REDIS_PASS=''

SLOW_PROXY_SWITCH = False
# 是否开启代理
PROXY_SWITCH = False