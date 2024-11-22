#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
'''
@Project ：spider_v9 
@File    ：test_rule.py
@IDE     ：PyCharm 
@INFO     ： 处理翻页请求到的结果，负责解析到详情部分
@Author  ：BGSPIDER
@Date    ：5/9/2024 下午3:56 
'''
import re
from typing import List, Dict
import jsonpath
from crawl.spiders.content_replace import *
from utils.tools import *


class ParseAction:
    """
    基本规则，初始化规则解析
    """

    def __init__(self):
        self.json_object = None
        self.text = ""
        # 实例化详情规则
        self.parse_detail_rule = DetailAction()

    def execute(self, response, rules_keys: str,base_rule):
        """
        rule入参为response rule，经过这个函数，对提取到对应的规则，为zip形式处理
        """
        parse_list = []
        rules=base_rule['rule_data']['rule_tree'][rules_keys]
        self.base_dict=base_rule
        parse_rule = rules['rules']
        requests_info=[]
        _len = 0
        for rule in parse_rule:
            if isinstance(rule,list):
                #这里应该是请求信息处理,此公告不实现，交给后面程序处理，需要将规则传递下去
                requests_info=rule
                continue
            if rule['fieldName']=='DESCRIPTION':
                pass
            values = self.parse_xpath_list(response, [rule],requests_info,rules_keys)
            if values['fieldName'] == 'SOURCE_URL':
                _len = len(values['spiderValue'])
            if _len <= 0 and values['fieldName'] == 'DESCRIPTION':
                _len = -1
            parse_list.append(values)
        if _len == -1:
            return parse_list
        else:
            parse_list = format_json(parse_list, _len)

            return parse_list

    def parse_xpath_list(self, response, rule_list,requests_info,rules_keys):
        """
        解析xpath
        """
        value_list = {}
        for _rules in rule_list:
            value_list['fieldName'] = _rules['fieldName']
            parse_type = _rules['spiderValueType']
            if parse_type == "XPATH":
                xpath_rule = _rules['xpath']
                value_list['spiderValue'] = parse_xpath_json_list(xpath_rule, response,_rules)
                # if _rules.get('regValue2') and value_list['spiderValue']:
                #     value_list['spiderValue'] = parse_re_list(_rules['regValue2'], value_list['spiderValue'])
            if parse_type == "REGEXP":
                re_rule = _rules['regValue']
                value_list['spiderValue'] = parse_re_list(re_rule, [response.text])

                # if _rules.get('replaces') and value_list['spiderValue']:
                #     for _replace in _rules['replaces']:
                #         value_list['spiderValue'] = parse_fromat_list(_replace['searchValue'], _replace['replaceValue'],
                #                                                       value_list['spiderValue'])
            if 'spiderValue' in value_list:
                _list = []
                for _ in value_list['spiderValue']:
                    # _需要转为字符串，并将requests_info传递下去
                    _list.append(self.parse_detail_rule.execute(_rules, _,response,requests_info,self.base_dict,rules_keys))
                value_list['spiderValue'] = _list
            if parse_type == "CONSTANT":
                value_list['CONSTANT'] = _rules['constantValue']
        return value_list


if __name__ == "__main__":
    demo = ParseAction()
    rule = {
        'rules': [
            {
                'containEnd': 0,
                'endStr': '',
                'fieldName': 'DESCRIPTION',
                'beforeValue': '',
                'containStart': 0,
                'unicodeFlag': 0,
                'afterValue': '',
                'xpath': '//*[@id="form1"]/div[6]/div/div[2]',
                'startStr': '',
                'visitFlag': 0,
                'regValue2Result': '',
                'id': 2134220,
                'filterTags': '',
                'plainFlag': 0,
                'spiderValueType': 'XPATH',
                'attFlag': 0,
                'pageReg': '',
                'stripFlag': 0,
                'filterFlag': 0,
                'replaces': [],
                'startToBorder': 0,
                'regValue2': '',
                'endToBorder': 0,
                'filterAtts': '',
                'attPatterns': [],
                'regValue': '',
                'spiderPosType': 'DETAIL',
                'sbcFlag': 0,
                'constantValue': ''
            },
            {
                'containEnd': 0,
                'endStr': '',
                'fieldName': 'PUBLISH_DATE',
                'beforeValue': '',
                'containStart': 0,
                'unicodeFlag': 0,
                'afterValue': '',
                'xpath': '//*[@id="form1"]/div[6]/div/div[1]/span[1]',
                'startStr': '',
                'visitFlag': 0,
                'regValue2Result': '',
                'id': 2134219,
                'filterTags': '',
                'plainFlag': 1,
                'spiderValueType': 'XPATH',
                'attFlag': 0,
                'pageReg': None,
                'stripFlag': 1,
                'filterFlag': 0,
                'replaces': [],
                'startToBorder': 0,
                'regValue2': '\\d{4}-\\d{2}-\\d{2}',
                'endToBorder': 0,
                'filterAtts': '',
                'attPatterns': [],
                'regValue': '',
                'spiderPosType': 'LIST',
                'sbcFlag': 0,
                'constantValue': ''
            }
        ]
    }
    text = ''
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
    }
    import requests, scrapy
    from scrapy.http import HtmlResponse


    def build_response(content_url):
        """生成scrapy response对象，测试使用"""
        res = requests.get(url=content_url, headers=headers)
        if res.status_code == 200:
            request = scrapy.Request(url=content_url)
            response = HtmlResponse(url=request.url, body=res.content, request=request, status=200)
            return response


    resp = build_response('http://www.fsigc.com:6116/notice_detail.aspx?id=HkIdW9RDhZ8WRr%2fQGJ6i9w%3d%3d')
    print(demo.execute(resp, rule))
