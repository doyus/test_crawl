#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
'''
@Project ：spider_v9 
@File    ：test_rule.py
@IDE     ：PyCharm 
@INFO     ： 对应v9的分页规则，处理翻页，等规则
@Author  ：BGSPIDER
@Date    ：5/9/2024 下午3:56 
'''
import re
from typing import List, Dict
import jsonpath
from utils.tools import *
class FirstUrl:
    """
    基本规则，初始化规则解析
    """
    def __init__(self):
        self.json_object = None
        self.text = ""
        self.base_dict={}
    def execute(self, rule):
        """
        rule为first_rule，只有入参规则，会生成对应的请求规则，对应规则为翻页，首次请求
        """
        self.json_object = rule
        req=self.format_first_url(self.json_object)
        return req
    def before_req(self,rules: dict):
        req_list = []
        start_url = rules['firstUrls']
        if start_url:
            #存在入口地址，
            if '\n' in start_url:
                #链接是多行
                start_url_list = start_url.split('\n')
            else:
                start_url_list = [start_url]
            for start_url in start_url_list:
                if not start_url:
                    #如果是空的话
                    continue
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
                        ###前置请求
                        req['type']=0
                req_list.append(req)
            return req_list
    def format_first_url(self,rules: dict,page_type='page') -> list:
        """
        格式化请求参数,初次请求格式化,最终返回列表,
        page_type判断当前是列表还是详情
        req实例
            {
                'url':"",
                'data:{},
                'json:{},
                'headers:{},
                'cookies:{},
            }
        """
        req_list = []
        req_list = []
        headers = {}
        #一般是多页配置
        if page_type=='page':
            start_url = rules['pageUrl']
        else:
            start_url = rules['detailUrl']
        if 'toInt()' in start_url:
            maxLoops = rules['maxLoops']
            if maxLoops>1:
                maxLoops=1
            for page in range(maxLoops):
                eval_str = start_url.replace('${i.toInt()', '{' + f"{page}")
                start_url = eval(f"f'{eval_str}'")
                req = {
                    'url': start_url
                }
                if rules['pagePost'] == 1:
                    req['method'] = 'POST'
                else:
                    req['method'] = 'GET'
                req_list.append(req)
        else:
            maxLoops = rules.get('maxLoops',1)
            if maxLoops>1:
                maxLoops=1
            for page in range(maxLoops):
                req = {
                    'url': start_url
                }
                if 'requestInfoes' in rules:#有请求参数
                    if rules['pagePost'] == 1:
                        req['method'] = 'POST'
                    else:
                        req['method'] = 'GET'
                    requestInfoes = rules['requestInfoes']
                    req_data={}
                    for infos in requestInfoes:
                        if infos['requestType'] == 'PAGE_PARAM' and  page_type=='page':
                            if rules['pagePost'] == 1:
                                req['method']='POST'
                            else:
                                req['method']='GET'
                            data = infos['value']
                            if '${i.toInt' in data:
                                data=form_data_loop(data=data,page=page)
                            if 'rest'  in infos['name']:
                                # req['data'] = format_str_to_dict(data)
                                req['type'],req['data'] = format_str_to_dict(data)
                            else:
                                req['type']=data
                                print(infos)
                                req_data[infos['name']]=infos['value']
                        elif infos['requestType'] == 'HEADER':
                            headers[infos['name']] = infos['value'].strip()
                            req['headers'] = headers
                        elif infos['requestType'] == 'DETAIL_PARAM' and  page_type=='detail':
                            if rules['pagePost'] == 1:
                                req['method']='POST'
                            else:
                                req['method']='GET'
                            data = infos['value']
                            if '${i.toInt' in data:
                                data=form_data_loop(data=data,page=page)
                            if 'rest'  in infos['name']:
                                # req['data'] = format_str_to_dict(data)
                                req['type'],req['data'] = format_str_to_dict(data)
                            else:
                                req['type']=data
                                req_data[infos['name']]=infos['value']
                    if req_data:
                        req['data']=req_data
                req_list.append(req)
        new_req_list = []
        for req in req_list:
            if 'sys.uuid()' in req['url']:
                req['url'] = req['url'].replace('${sys.uuid()}', str(uuid4()))
            if 'method' not in req:
                req['method']='GET'
            new_req_list.append(req)
        logging.info(new_req_list)
        return new_req_list
if __name__ == "__main__":
    demo=FirstUrl()
    rule={
            "repeats": [{"repeatFlag": 1, "sourceFieldNames": ["SOURCE_URL"], "repeatPosType": "LIST", "freshFlag": 0}],
            "detailLocalRedirect": 0,
            "adviceMultiple": None,
            "limitDay": None,
            "configType": "GUIDE",
            "type": "AUTO",
            "enterUrl": "",
            "maxLoops": 1,
            "modifyTime": None,
            "rank": None,
            "id": 1942721,
            "pageLocalRedirect": 0,
            "runStrategy": "INTERVAL",
            "detailPost": 0,
            "optimizeNum": None,
            "soTimeout": 120000,
            "attSoTimeout": 600000,
            "name": "(三级)湖北-国资优采云平台-招标采购",
            "singleFlag": 0,
            "detailUrl": None,
            "htmlToXmlConfig": "namespaces-aware=\"False\"",
            "code": "T20231222105808220",
            "attTry": 1,
            "singleServer": None,
            "configFlag": 0,
            "rule": None,
            "remark": "",
            "firstUrls": "",
            "runInterval": 3,
            "runCount": 0,
            "connectionTimeout": 10000,
            "runCron": "",
            "retryCount": 3,
            "filters": [],
            "releaseNum": None,
            "longCut": 1,
            "spiderDepth": None,
            "url": "",
            "timeStamp": "0",
            "detailParamName": None, "createTime": "2023-12-22 11:39:59", "limitFieldName": "", "pagePost": 1,
            "requestInfoes": [{"requestType": "PAGE_PARAM", "name": "rest", "requestValueType": "DIRECT",
                               "value": "cityCode=central&title=&dataCode=2114&queryDay=-1&infoSource=&type=-1&pageSize=30&pageNumber=1"}],
            "pageUrl": "https://www.gzycy.com/portal/project_notice_info/list#rest",
            "channel": {"text": "招标信息", "value": 5269},
            "dataType": {"text": "通用类别", "value": 1250},
            "site": {"text": "国资优采云平台[https://www.gzycy.com/portal/central]", "value": 1941971},
            "region": {"text": "/全国/湖北省", "value": 1823}, "intervalUnit": {"text": "小时", "value": "HOUR"},
            "cookiePolicy": {"text": "rfc2109", "value": "RFC_2109"},
        }
    print(demo.execute(rule))

