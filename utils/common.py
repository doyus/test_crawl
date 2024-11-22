#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
'''
@Project ：gxcx_crawl 
@File    ：common.py
@IDE     ：PyCharm 
@INFO     ： 公共函数
@Author  ：BGSPIDER
@Date    ：14/12/2023 下午3:03 
'''
import re
import time
import types
import random
import hashlib
from urllib import parse

import scrapy


def run_func_generator(spider, response, str_func_generator):
    """
    :param response: scrapy.response
    :param str_func_generator:str函数
    :return: list
    """
    module_name = re.findall('https?://(.*?)/', response.url)[0]
    hash = hashlib.sha1()
    hash.update(str(module_name).encode('utf-8'))
    module_hash = hash.hexdigest()
    module = types.ModuleType(module_hash)
    func_str = str_func_generator
    exec(func_str, module.__dict__)
    result_list = module.generator(response)
    return result_list


def get_url_md5(url):
    """
    对url进行md5, 用于去重
    :param url:
    :return:
    """
    if isinstance(url, str):
        return hashlib.md5(url.encode('utf-8')).hexdigest()


def get_url_domain(url):
    """获取 URL 中的域名"""
    if isinstance(url, str):
        domain = parse.urlparse(url).netloc
        return domain


def get_timestamp():
    """获取13位时间戳"""
    return int(time.time() * 1000)


def get_save_path(url):
    """
    对url进行切割  用于存储
    :param url:
    :return: 存储路径
    """
    try:
        path = re.findall(r'https?://(.*)', url)[0]
    except BaseException as e:
        try:
            path = re.findall(r'ftp://(.*)', url)[0]
        except BaseException as e:
            raise BaseException('存储路径获取失败==url>{} ==error>{}'.format(url, e))
    return path

