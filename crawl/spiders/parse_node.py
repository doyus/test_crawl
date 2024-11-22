#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
'''
@Project ：crawl 
@File    ：parse_node.py
@IDE     ：PyCharm 
@INFO     ： 
@Author  ：BGSPIDER
@Date    ：29/12/2023 下午3:12 
'''
import json
import re

from scrapy.selector import Selector
import scrapy
from scrapy.http import HtmlResponse
import jsonpath
from utils.tools import *
import logging
from uuid import uuid4
from utils.mysql_db import *
from devtool.util import *

def parse_re_list(rule: str, response: list):
    """
    解析re规则
    """
    _value = []
    for _ in response:
        x = re.findall(rule, _,re.S)
        for _x in x:
            _value.append(_x)
    return _value


def parse_xpath_json_list(rule: str, response):
    """
    解析xpath规则和json
    """
    try:
        if get_response_type(response) == 'text':
            if rule=='/':
                _value=response.text
            else:
                # bs_brokenhtml
                completed_html=bs_brokenhtml(response.text)
                _value =etree.HTML(completed_html).xpath(rule)
        else:
            rule = rule.replace('//', '$..')
            _value = jsonpath.jsonpath(response.json(), rule)
        return _value
    except Exception as e:
        _value = []
    return _value


def parse_fromat_list(serach_str: str, replace_str: str, response: str):
    """
    替换字符串,正则、replace
    """
    try:
        _serach = re.search(serach_str, response).groups()
        for _ in range(len(_serach)):
            replace_str = replace_str.replace(f'${_ + 1}', _serach[_])
        return replace_str
    except Exception as e:
        logging.error(e)
    return response


def parse_replace_list(rules: list, response: str):
    """
    替换字符串
    """
    new_str = ''
    for rule in rules:
        replaceValue = rule['replaceValue']
        new_re_str = re.search(rule['searchValue'], response)
        if not new_re_str:
            new_str += replaceValue + response
    return new_str


def content_processing(response_list: str, rule, response_content):
    """
    内容处理
    """
    new_response = []
    if isinstance(response_list, str):
        resp_type = 'list'
        response_list = [response_list]
    if rule['fieldName']=='SOURCE_URL':
        response_list=fromat_url(rule,response_list,response_content)
    for response in response_list:
        if rule['replaces']:
            for rep in rule['replaces']:
                if rep['searchFlag'] == 0:
                    if rep['replaceFlag'] == 1:
                        # if re.search(rep['searchValue'], response):
                            response = response.replace(rep['searchValue'], rep['replaceValue'])
                        # else:
                        #     if '<\\/' not in rep['searchValue']:
                        #         pass
                        #     else:
                        #         response=response+rep['replaceValue']

                    else:
                        response = re.sub(rep['searchValue'], rep['replaceValue'], response, count=1)
                else:
                    replaceValue = rep['replaceValue']
                    searchValue = rep['searchValue']
                    if rep['replaceFlag'] == 1:
                        while True:
                            re_serach = re.search(searchValue, response)
                            if re_serach:
                                # response = rep['replaceValue']
                                re_serach = re_serach.group()
                                if '$' in rep['replaceValue']:
                                    li_x = re.findall('(\$\d{1})', rep['replaceValue'])
                                    if li_x:
                                        for _ in li_x:
                                            response = response.replace(_, re_serach[int(_.replace('$', '')) - 1])
                                else:
                                    response = response.replace(re_serach, replaceValue)
                            else:
                                break
        if rule['plainFlag']:
            response = html_to_str(response)
        if rule['stripFlag']:
            response = response.strip()
        if rule['beforeValue']:
            response = rule['beforeValue']+response
        if rule['afterValue']:
            response = response+rule['afterValue']
        new_response.append(response)
    if isinstance(response_list, str):
        return new_response[0]
    else:
        return new_response


def parse_xpath_list(response, rule_list):
    """
    解析xpath
    """
    value_list = {}
    for _rules in rule_list:
        value_list['fieldName'] = _rules['fieldName']
        parse_type = _rules['spiderValueType']
        if parse_type == "XPATH":
            xpath_rule = _rules['xpath']
            value_list['spiderValue'] = parse_xpath_json_list(xpath_rule, response)
            if _rules.get('regValue2') and value_list['spiderValue']:
                value_list['spiderValue'] = parse_re_list(_rules['regValue2'], value_list['spiderValue'])
        if parse_type == "REGEXP":
            re_rule = _rules['regValue']
            value_list['spiderValue'] = parse_re_list(re_rule, [response.text])[0]
            # if _rules.get('replaces') and value_list['spiderValue']:
            #     for _replace in _rules['replaces']:
            #         value_list['spiderValue'] = parse_fromat_list(_replace['searchValue'], _replace['replaceValue'],
            #                                                       value_list['spiderValue'])
        if 'spiderValue' in value_list:
            value_list['spiderValue'] = content_processing(value_list['spiderValue'], _rules, response)
        if parse_type == "CONSTANT":
            value_list['CONSTANT'] = _rules['constantValue']
    return value_list


def format_json(detail_json, _len):
    """
    重新格式化整体数据样式,列表页包装
    """
    len_number = []
    for num in range(_len):
        _dict = {}
        for x in range(len(detail_json)):
            if 'spiderValue' in detail_json[x]:
                if len(detail_json[x]['spiderValue'])==1:
                    _dict[detail_json[x]['fieldName']] = detail_json[x]['spiderValue'][0]
                else:
                    _dict[detail_json[x]['fieldName']] = detail_json[x]['spiderValue'][num]
            if 'CONSTANT' in detail_json[x]:
                _dict[detail_json[x]['fieldName']] = detail_json[x]['CONSTANT']
        len_number.append(_dict)
    return len_number

def format_str_to_dict(str_t):
    """
    将一行data转为data
    :param str_t:
    :return:
    """
    try:
        new_dict = {}
        if '&' in str_t:
            _ = str_t.split('&')
            for _x in _:
                new_dict[_x.split('=')[0]] = _x.split('=')[1]
            return new_dict
        try:
            new_dict=json.loads(str_t)
            return new_dict
        except Exception as e:
            pass
    except Exception as e:
        return str_t
def fromat_url(rules, values, response):
    """
    格式化url，拼接url或者替换规则
    """
    new_values = []
    if rules['replaces']:
        for _response in values:
            for rep in rules['replaces']:
                if rep['searchFlag'] == 0:
                    if rep['replaceFlag'] == 1:
                        # if re.search(rep['searchValue'], response):
                            _response = _response.replace(rep['searchValue'], rep['replaceValue'])
                        # else:
                        #     if '<\\/' not in rep['searchValue']:
                        #         pass
                        #     else:
                        #         response=response+rep['replaceValue']
                    else:
                        _response = re.sub(rep['searchValue'], rep['replaceValue'], response, count=1)
                else:
                    replaceValue = rep['replaceValue']
                    searchValue = rep['searchValue']
                    if rep['replaceFlag'] == 1:
                        while True:
                            re_serach = re.search(searchValue, _response)
                            if re_serach:
                                # response = rep['replaceValue']
                                re_serach = re_serach.group()
                                if '$' in rep['replaceValue']:
                                    li_x = re.findall('(\$\d{1})', rep['replaceValue'])
                                    if li_x:
                                        for _ in li_x:
                                            _response = _response.replace(_, re_serach[int(_.replace('$', '')) - 1])
                                else:
                                    _response = _response.replace(re_serach, replaceValue)
                            else:
                                break
            new_values.append(_response)
    else:
        for _value in values:
            if 'http' not in _value:
                _url = response.urljoin(_value)
            else:
                _url=_value
            new_values.append(_url)
    return new_values


def parse_tree(rules: dict, detail_content, **keywords):
    """
    解析树
    """
    parse_list = []
    parse_rule = rules['rules']
    _len = 0
    for rule in parse_rule:
        values = parse_xpath_list(detail_content, [rule])
        if values['fieldName'] == 'SOURCE_URL':
            _len = len(values['spiderValue'])
        if _len<=0 and  values['fieldName'] == 'DESCRIPTION':
            _len = -1
        parse_list.append(values)
    if _len == -1:
        return parse_list
    else:
        parse_list = format_json(parse_list, _len)
        return parse_list


def v9_new_json(config_json):
    """
    v9转为正常格式数据
    """
    new_json = {
        "rule_data": {
            "first_rules": {},
            "rule_tree": {
                "list_rule": {
                    "rules": [
                    ]
                },
                "detail_rule": {
                    "rules": [

                    ]
                }
            }
        }
    }
    old_json = config_json['data']
    for _key in old_json.keys():
        if _key=='requestInfoes':
            new_json['rule_data']['rule_tree']['list_rule']['rules'].append(old_json[_key])
        if isinstance(old_json[_key], dict):
            if 'spiderPosType' in old_json[_key]:
                if old_json[_key]['spiderPosType'] == 'LIST':
                    new_json['rule_data']['rule_tree']['list_rule']['rules'].append(old_json[_key])
                if old_json[_key]['spiderPosType'] == 'DETAIL':
                    new_json['rule_data']['rule_tree']['detail_rule']['rules'].append(old_json[_key])
            else:
                new_json['rule_data']['first_rules'][_key] = old_json[_key]
        else:
            new_json['rule_data']['first_rules'][_key] = old_json[_key]
    return new_json


def fromat_first_url(rules: dict) -> list:
    """
    格式化请求参数,初次请求格式化,最终返回列表,
    req实例
        {
            'url':"",
            'data:{},
            'json:{},
            'headers:{},
            'cookies:{},
        }
    """
    # 'https://cqjy.huizhou.gov.cn/Web/Index?page=1\nhttps://cqjy.huizhou.gov.cn/Web/Index?page=2\nhttps://cqjy.huizhou.gov.cn/Web/Index?page=3\nhttps://cqjy.huizhou.gov.cn/Web/Index?page=4'
    req_list = []
    start_url = rules['firstUrls']
    if start_url:
        if '\n' in start_url:
            start_url_list=start_url.split('\n')
        else:
            start_url_list=[start_url]
        for start_url in start_url_list:
            req = {
                'url': start_url
            }
            if 'requestInfoes' in rules:
                requestInfoes = rules['requestInfoes']
                for infos in requestInfoes:
                    if infos['requestType'] == 'PAGE_PARAM':
                        data = infos['value']
                        req['data'] = format_str_to_dict(data)
                    if infos['requestType'] == 'HEADER':
                        headers = {}
                        headers[infos['name']] = infos['value']
                        req['headers'] = headers
            req_list.append(req)
    else:
        start_url = rules['pageUrl']
        if 'toInt()' in start_url:
            maxLoops = rules['maxLoops']
            for page in range(maxLoops):
                eval_str = start_url.replace('${i.toInt()', '{' + f"{page}")
                start_url = eval(f"f'{eval_str}'")
                req = {
                    'url': start_url
                }
                req_list.append(req)
        else:
            req = {
                'url': start_url
            }
            if 'requestInfoes' in rules:
                requestInfoes = rules['requestInfoes']
                for infos in requestInfoes:
                    if infos['requestType'] == 'PAGE_PARAM':
                        data = infos['value']
                        req['data'] = format_str_to_dict(data)
                    if infos['requestType'] == 'HEADER':
                        headers = {}
                        headers[infos['name']] = infos['value']
                        req['headers'] = headers
            req_list.append(req)
    new_req_list = []
    for req in req_list:
        if 'sys.uuid()' in req['url']:
            req['url'] = req['url'].replace('${sys.uuid()}', str(uuid4()))
        new_req_list.append(req)
    logging.info(new_req_list)
    return new_req_list
def get_task(site_id):
    """
    判断id是否存在
    """
    sql = 'SELECT config FROM bgspider_task WHERE id = %s'
    cursor.execute(sql, (site_id))
    data = cursor.fetchall()
    if data:
        return json.loads(data[0][0])
    else:
        return []

# def update_crawl_num(site_id):
