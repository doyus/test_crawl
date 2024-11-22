#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
'''
@Project ：pyqt5_spider 
@File    ：spider.py
@IDE     ：PyCharm 
@INFO     ： 采集模块
@Author  ：BGSPIDER
@Date    ：19/2/2024 上午9:51
'''
import copy
import random
import time
from tkinter import filedialog, ttk
from DrissionPage import ChromiumPage, ChromiumOptions
from lxml.html import fromstring, tostring
from DrissionPage import WebPage
from DrissionPage import ChromiumOptions
import tkinter.messagebox
import json
import xml.etree.ElementTree as ET
import requests
from devtool.tools import *
from devtool.conf import *
from logger import logging as log2
from lxml import etree
import logging, re
import sqlite3
import threading
from devtool.parse_node import *
from devtool.conf import *
class CRAWL_DRIVER:
    def __init__(self):
        self.log=log2
        pass
    def get_config(self):
        # 'https://ggzyjy.sc.gov.cn/jyxx/transactionInfo.html'
        # with open('config/test.')
        self.config={
            "extension":['proxy'],
            "user_path":'../user_path',
            "run_list":['start_url','click_element_0','click_element_1','click_element_2','cycle_acquisition_elements','loop_page_turning'],
            "run_list_zh":['首页地址','点击栏目','点击栏目','点击栏目','循环提取元素','翻页'],
            "start_rule":{
                "rules":
                    {"start_url":"https://www.hfgdjt.com/"}
            },
            "deduplication":{
                "field":"title",
                "position":"detail",
            },
            "click_rule":{
                "0":{
                "ele": "text=招标采购",
                 "sleep":0,
                 "wait_type":"dom",
                 },
                "1": {
                    "ele": "text=招标公告",
                    "sleep": 0,
                    "wait_type": "dom",
                },
                "2": {
                    "ele": "text=服务类",
                    "sleep": 0,
                    "wait_type": "dom",
                }
            },
            "list_rule":{
                "crawl_type":"click",
                "rules":[
                    {
                        "xpath": "//div[@class='list-doc-r ']/ul//li//h3",
                        "remove_xpath":[],
                        "type":'html',
                        "endStr": "",
                        "attFlag": 0,
                        "pageReg": None,
                        "sbcFlag": 0,
                        "regValue": "",
                        "replaces": [],
                        "startStr": "",
                        "fieldName": "SOURCE_URL",
                        "plainFlag": 0,
                        "regValue2": "",
                        "stripFlag": 1,
                        "visitFlag": 0,
                        "afterValue": "",
                        "containEnd": 0,
                        "filterAtts": "",
                        "filterFlag": 0,
                        "filterTags": "",
                        "attPatterns": [],
                        "beforeValue": "",
                        "endToBorder": 0,
                        "unicodeFlag": 0,
                        "containStart": 0,
                        "constantValue": "",
                        "spiderPosType": "LIST",
                        "startToBorder": 0,
                        "regValue2Result": "",
                        "spiderValueType": "CLICK"
                    }
                ]
            },
            "detail_rule":{
                "rules":[
                    {
                        "xpath": "//div[@class=\"article-r \"]",
                        "remove_xpath":[],
                        "type":'html',
                        "endStr": "",
                        "attFlag": 0,
                        "pageReg": None,
                        "sbcFlag": 0,
                        "regValue": "",
                        "replaces": [],
                        "startStr": "",
                        "fieldName": "DESCRIPTION",
                        "plainFlag": 0,
                        "regValue2": "",
                        "stripFlag": 1,
                        "visitFlag": 0,
                        "afterValue": "",
                        "containEnd": 0,
                        "filterAtts": "",
                        "filterFlag": 0,
                        "filterTags": "",
                        "attPatterns": [],
                        "beforeValue": "",
                        "endToBorder": 0,
                        "unicodeFlag": 0,
                        "containStart": 0,
                        "constantValue": "",
                        "spiderPosType": "LIST",
                        "startToBorder": 0,
                        "regValue2Result": "",
                        "spiderValueType": "XPATH"
                    }
                ]
            },
            "loop_page_turning":{
                "next_click":{
                    'type':"XPATH",
                    "max_page":10,
                    "timeout":5,
                    "xpath":"(//a[contains(text(),'>')])[1]",
                }
            }
        }
    def start_page(self):
        co = ChromiumOptions()
        if self.config['extension']:
            for extension in self.config['extension']:
                co.add_extension(f'../extension/{extension}')
            self.log.info('插件增加完毕')
        if self.config.get('user_path'):
            co.set_user_data_path(self.config.get('user_path'))
            self.log.info('用户信息加载完毕')
        self.page = ChromiumPage(co)
        # self.page.get('https://www.ip138.com/')
    def hand_list(self):
        self.page.wait.doc_loaded()
        time.sleep(5)
        response = self.page.html
        now_url = self.page.url
        content=parse_tree(self.config['list_rule'], response,now_url)
        print(content)
        for i in range(len(content)):
            ele = self.page.eles('xpath:' + '//div[@class=\'list-doc-r \']/ul//li//h3')
            ele2=ele[i]
            ele2.click()
            self.page.wait.doc_loaded()
            time.sleep(5)
            self.head_detail(content[i])
            self.page.back()
            self.page.wait.doc_loaded()
            break
        # for detail in content:
        #     if Setting.reduce_repeat([{'url':detail['SOURCE_URL']}]):
        #         self.head_detail(detail)
        #     else:
        #         self.log.debug('当前公告已经存在')
    def head_detail(self,detail):
        self.page.wait.doc_loaded()
        response = self.page.html
        now_url = self.page.url
        detail_list = parse_tree(self.config['detail_rule'], response,now_url)
        print(detail_list)
        for _detail in detail_list:
            if _detail['fieldName']=='DESCRIPTION':
                if _detail['spiderValue']:
                    detail_html=''.join(_detail['spiderValue'])
                    print(detail_html)
    def head_home(self):
        start_url=self.config['start_rule']['rules']['start_url']
        self.page.get(start_url)
        self.page.wait.doc_loaded()
    def save_cms(self,insert_d):
        self.log.debug(insert_d)
    def click_element(self,id):
        """
        点击元素
        :return:
        """
        rules=self.config['click_rule'][id]
        print(rules)
        ele=self.page.ele(rules['ele'])
        ele.click()
        self.page.wait.doc_loaded()
    def hand_page(self):
        """
        翻页配置
        :return:
        """
        rules=self.config['loop_page_turning']
        if 'next_click' in rules:
            _rule=rules['next_click']
            max_page=_rule.get('max_page')
            for x in range(max_page):
                if _rule['type']=='XPATH':
                    self.page.ele('xpath:'+_rule['xpath']).click()
                    self.page.wait.doc_loaded()
                    _time=get_value(_rule,'timeout',3)
                self.hand_list()
    def run(self):
        self.get_config()
        self.start_page()
        run_task=self.config['run_list']
        for task in run_task:
            print(task)
            if task=='start_url':
                self.head_home()
            if 'click_element' in task:
                id=task.split('_')[-1]
                self.click_element(id)
            if 'cycle_acquisition_elements' in task:
                self.hand_list()
            if 'loop_page_turning' in task:
                self.hand_page()
        # ele=self.page.ele('xpath:/html/body/div[4]/div/div[2]/ul/li[3]/h3')
        # ele.click()
        # time.sleep(10)
        # self.page.back()
        # input()
if __name__ == "__main__":
    demo = CRAWL_DRIVER()
    demo.run()